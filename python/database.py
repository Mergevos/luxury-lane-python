import mysql.connector
import importlib
import sys
from mysql.connector import Error
from pysamp import *

class Database:

    # Handles database connection

    _host = "127.0.0.1"
    _user = "root"
    _port = "3306"
    _password = ""
    _database = "luxury-life"

    _connection = None

    # Connects to a database
    @classmethod
    def connect(cls):
        try:
            cls._connection = mysql.connector.connect(
                host=cls._host,
                user=cls._user,
                port=cls._port,
                password=cls._password,
                database=cls._database
            )
            print('Connected to database')
        except Error as e:
            if isinstance(e, mysql.connector.errors.InterfaceError):
                print("Error: There was a problem with the database connection. Couldn't connect.")
            
            else:
                print(f"Error: {e}")
    
    # Gets connection
    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls.connect()

        return cls._connection
    
    # Executes a query
    @classmethod
    def get_cursor(cls, as_dictionary=False):
        return cls._connection.cursor(dictionary=as_dictionary)

    # Closes the connection
    @classmethod
    def close_connection(cls):
        if cls._connection:
            cls._connection.close()
            print('Closed connection')

        else:
            print('Not connected')


@on_gamemode_init
def on_start():
    Database.connect()
    return 1


@on_gamemode_exit
def on_stop():
    Database.close_connection()
    print('Unloading gamemode')
    return 1
    