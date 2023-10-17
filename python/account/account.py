from samp import NO_TEAM
from python.player.player import Player, MESSAGE_ANNOUNCEMENT
from pysamp.dialog import Dialog
from python.database import Database
from dataclasses import dataclass

import mysql.connector
import bcrypt
import re

GENDER_MALE = 1
GENDER_FEMALE = 2

@dataclass
class Account:
    sqlid = None
    password = None
    age = None
    _gender = None
    _email = None

    mute = False
    muted_until = None

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        else:
            self._email = email
        
    @property
    def gender(self) -> int:
        return self._gender
    
    @gender.setter
    def gender(self, gender: int):
        if gender in (GENDER_MALE, GENDER_FEMALE):
            self._gender = gender
        else:
            raise ValueError("Invalid gender input")
    



# Register
@Player.using_pool
def register_response(player: Player, response: int, listitem: int, input: str):
    if response:

        if len(input) < 6:
            return Dialog.create(type=3, title='Luxury Lane', content='Ops,\ncini se da ste uneli lozinku ispod 6 znakova. Molimo Vas unesite lozinku sa vise znakova.', button_1='Unesi', button_2='Izlaz', on_response=register_response).show(player)
        
        salt = bcrypt.gensalt()  # Generate a random salt
        hashed = bcrypt.hashpw(input.encode("utf-8"), salt)  # Hash the password
        account = player.account
        account.password = hashed
        Dialog.create(type=0, title='Luxury Lane', content='Nastavite sa registracijom molim Vas. Odaberite Vas pol.', button_1='Musko', button_2='Zensko', on_response=gender_select).show(player)
   
    else:
        player.kick() 

@Player.using_pool
def gender_select(player: Player, response: int, listitem: int, input: str):
    account = player.account

    if response:
        account.gender = GENDER_MALE
        Dialog.create(type=1, title='Luxury Lane', content='Nastavite sa registracijom molim Vas. Molimo unesite Vas email.', button_1='Unesi', button_2='Izlaz', on_response=email_input).show(player)
   
    else:
        account.gender = GENDER_FEMALE
        Dialog.create(type=1, title='Luxury Lane', content='Nastavite sa registracijom molim Vas. Molimo unesite Vas email.', button_1='Unesi', button_2='Izlaz', on_response=email_input).show(player)


@Player.using_pool
def email_input(player: Player, response: int, listitem: int, input: str):
    account = player.account

    if response:
        
        try:
            account.email = input
        except ValueError as error:
            return Dialog.create(type=1, title='Luxury Lane', content='Uneli ste nepravilan email. Molimo unesite Vas email.', button_1='Unesi', button_2='Izlaz', on_response=email_input).show(player)
        
        Dialog.create(type=1, title='Luxury Lane', content='Unesite Vase godine.', button_1='Unesi', button_2='Izlaz', on_response=handle_age).show(player)

    else:
        player.kick()

@Player.using_pool
def handle_age(player: Player, response: int, listitem: int, input: str):
    if response:
        account = player.account
        if not input.isdigit() or not (18 <= int(input) <= 70):
            return Dialog.create(type=1, title='Luxury Lane', content='Godine moraju biti pozitivan broj od 18-70...', button_1='Unesi', button_2='Izlaz', on_response=handle_age).show(player)
        
        account.age = int(input)

        try:
            skin = 30
            connection = Database.get_connection()
            cursor = Database.get_cursor()
            cursor.execute("INSERT INTO account (account_name, account_email, account_password, account_gender, account_skin, account_age) VALUES (%s, %s, %s, %s, %s, %s)", (player.get_name(), account.email, account.password, account.gender, skin, account.age, ))
            connection.commit()
            player.set_spawn_info(NO_TEAM, skin, 10.0, 10.0, 10.0, 10.0, 0, 0, 0, 0, 0, 0)
            account.sqlid = cursor.lastrowid
            player.toggle_spectating(False)

        except Exception as e:
            print(f"Error during database insertion: {e}") 

        
    else:
        player.kick()

# Login 
@Player.using_pool
def login_response(player: Player, response: int, listitem: int, input: str):
    if response:
        account = player.account
        if bcrypt.checkpw(input.encode("utf-8"), account.password.encode("utf-8")):
            # Correct
            handle_spawn(player)

        else:
            # Not correct
            Dialog.create(type=3, title='Luxury Lane', content=f'Ooops {player.get_name()}\nIzgleda da ste uneli pogresan password. Pokusajte ponovo.', button_1='Unesi', button_2='Izlaz', on_response=login_response).show(player)
    else:
        player.kick() 

@Player.using_pool
def handle_spawn(player: Player):
    
    account = player.account
    account.password = None
    cursor = Database.get_cursor(as_dictionary=True)
    cursor.execute("SELECT * FROM account LEFT JOIN account_muted ON account.account_id = account_muted.account_mute_id WHERE account.account_name = %s", (player.get_name(),))
    
    row = cursor.fetchone()
    if row:
        account.password = None # Clear the password from data
        account.sqlid = row['account_id']
        account.gender = row['account_gender']
        account.age = row['account_age']
        skin = row['account_skin']

        account.mute = False if row['account_mute_id'] is None else True
        account.muted_until = row['account_mute_until']
        player.set_spawn_info(NO_TEAM, skin, 10.0, 10.0, 10.0, 10.0, 0, 0, 0, 0, 0, 0)
        player.toggle_spectating(False)
        if account.mute: 
            player.message_send(MESSAGE_ANNOUNCEMENT, 'Vi ste mutirani. Ne mozete koristiti komande i cet.')

     
# Checking
@Player.on_request_class
@Player.using_pool
def on_player_request_class(player: Player, classid: int):
    player.toggle_spectating(True)
    player.account = Account()
    cursor = Database.get_cursor()
    cursor.execute("SELECT account_password FROM account WHERE account_name = %s", (player.get_name(),))
    row = cursor.fetchone()
    
    if row is None:
        Dialog.create(type=3, title='Luxury Lane', content=f'Dobrodosli {player.get_name()}\nDrago nam je da ste dosli na nas server. Da biste nastavili, molimo Vas unesite Vasu zeljenu lozinku.', button_1='Unesi', button_2='Izlaz', on_response=register_response).show(player)
        pass
    else:
        account = player.account
        account.password = row[0]
        Dialog.create(type=3, title='Luxury Lane', content=f'Dobrodosli {player.get_name()}\nDrago nam je da ste dosli na nas server. Da biste nastavili, molimo Vas unesite Vasu sacuvanu lozinku.', button_1='Unesi', button_2='Izlaz', on_response=login_response).show(player)
    
    return 0
