from python.player import Player as CustomPlayer
from pysamp import send_client_message, toggle_player_spectating
from pysamp.dialog import Dialog
from pysamp.player import Player
from python.database import Database
import mysql.connector
import bcrypt
import re

GENDER_MALE = 1
GENDER_FEMALE = 2

class Account(CustomPlayer):
    _password = None
    _age = None
    _gender = None
    _email = None

    def __init__(self, player_id):
        super().__init__(player_id)

    @classmethod
    def set_password(cls, password: str):
        cls._password = password
        
    @classmethod
    def get_password(cls) -> str:
        return cls._password

    @classmethod
    def set_email(cls, email: str):
        cls._email = email
        
    @classmethod
    def get_email(cls) -> str:
        return cls._email
    
    @classmethod 
    def set_age(cls, age: int):
        cls._age = age
    
    @classmethod
    def get_age(cls) -> int:
        return cls._age

    @classmethod 
    def set_gender(cls, gender: int):
        if gender is GENDER_MALE or GENDER_FEMALE:
            cls._gender = gender
    
    @classmethod
    def get_gender(cls) -> int:
        return cls._gender


# Register
@CustomPlayer.using_pool
def register_response(player: CustomPlayer, response: int, listitem: int, input: str):
    if response:
        if len(input) < 6:
            return Dialog.create(type=3, title='Luxury Lane', content=f'Welcome {player.get_name()}\nWe are pleased to have you here. In order to continue, please input your desired password.', button_1='Input', button_2='Exit', on_response=register_response).show(player)
        
        salt = bcrypt.gensalt()  # Generate a random salt
        hashed = bcrypt.hashpw(input.encode("utf-8"), salt)  # Hash the password
        Account.set_password(hashed)
        Dialog.create(type=0, title='Luxury Lane', content='Nastavite sa registracijom molim Vas. Odaberite Vas pol.', button_1='Musko', button_2='Zensko', on_response=gender_select).show(player)
    else:
        player.kick() 

@CustomPlayer.using_pool
def gender_select(player: CustomPlayer, response: int, listitem: int, input: str):
    if response:
        Account.set_gender(GENDER_MALE)
        Dialog.create(type=1, title='Luxury Lane', content='Nastavite sa registracijom molim Vas. Molimo unesite Vas email.', button_1='Musko', button_2='Zensko', on_response=email_input).show(player)
    else:
        Account.set_gender(GENDER_FEMALE)
        Dialog.create(type=1, title='Luxury Lane', content='Nastavite sa registracijom molim Vas. Molimo unesite Vas email.', button_1='Musko', button_2='Zensko', on_response=email_input).show(player)


@CustomPlayer.using_pool
def email_input(player: CustomPlayer, response: int, listitem: int, input: str):
    if response:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, input):
            return Dialog.create(type=1, title='Luxury Lane', content='Uneli ste nepravilan email. Molimo unesite Vas email.', button_1='Musko', button_2='Zensko', on_response=email_input).show(player)
        Account.set_email(input)
        player.set_skin(30)
        try:
            connection = Database.get_connection()
            cursor = Database.get_cursor()
            cursor.execute("INSERT INTO account (account_name, account_email, account_password, account_gender, account_skin) VALUES (%s, %s, %s, %s, %s)", (player.get_name(), Account.get_email(), Account.get_password(), Account.get_gender(), player.get_skin(), ))
            connection.commit()
        except Exception as e:
            print(f"Error during database insertion: {e}") 
        player.toggle_spectating(False)
        player.spawn()
    else:
        Account.set_gender(GENDER_FEMALE)

# Login 
@CustomPlayer.using_pool
def login_response(player: CustomPlayer, response: int, listitem: int, input: str):
    if response:
        if bcrypt.checkpw(input.encode("utf-8"), Account.get_password().encode("utf-8")):
            # Correct
            player.toggle_spectating(False)
            player.spawn()
            Account.set_password(None)
        else:
            # Not correct
            Dialog.create(type=3, title='Luxury Lane', content=f'Ooops {player.get_name()}\nIzgleda da ste uneli pogresan password. Pokusajte ponovo.', button_1='Input', button_2='Exit', on_response=login_response).show(player)
    else:
        player.kick() 


# Checking
@Player.on_request_class
@CustomPlayer.using_pool
def on_player_request_class(player: CustomPlayer, classid: int):
    player.toggle_spectating(True)
    cursor = Database.get_cursor()
    cursor.execute("SELECT account_password FROM account WHERE account_name = %s", (player.get_name(),))
    row = cursor.fetchone()
    if row is None:
        Dialog.create(type=3, title='Luxury Lane', content=f'Welcome {player.get_name()}\nWe are pleased to have you here. In order to continue, please input your desired password.', button_1='Input', button_2='Exit', on_response=register_response).show(player)
    else:
        Account.set_password(row[0])
        Dialog.create(type=3, title='Luxury Lane', content=f'Welcome {player.get_name()}\nWe are pleased to have you here. In order to continue, please input your saved password.', button_1='Input', button_2='Exit', on_response=login_response).show(player)
    return 0

