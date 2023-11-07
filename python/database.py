import mysql.connector
import importlib
import sys
from mysql.connector import Error
from pysamp import *

class Database:

    # Handles database connection

    host = "127.0.0.1"
    user = "root"
    port = "3306"
    password = ""
    database = "luxury-life"

    _connection = None

    # Connects to a database
    @classmethod
    def connect(cls):
        try:
            cls._connection = mysql.connector.connect(
                host=cls.host,
                user=cls.user,
                port=cls.port,
                password=cls.password,
                database=cls.database
            )
            print('Connected to database')
        except Error as e:
            if isinstance(e, mysql.connector.errors.InterfaceError):
                print("Error: There was a problem with the database connection. Couldn't connect.")
            
            else:
                print(f"Error: {e}")
    
    # Gets connection
    @classmethod
    @property
    def connection(cls):
        if cls._connection is None:
            cls.connect()

        return cls._connection

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


@on_gamemode_exit
def on_stop():
    Database.close_connection()
    print('Unloading gamemode')
