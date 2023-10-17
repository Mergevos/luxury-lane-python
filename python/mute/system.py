import samp
from python.account.account import Account
from pysamp import set_timer, on_gamemode_init
from python.database import Database


def check_for_unmute():
    
    connection = Database.get_connection()
    cursor = Database.get_cursor()
    cursor.execute('DELETE FROM account_muted WHERE account_mute_until IN (SELECT account_mute_until FROM account_muted WHERE account_mute_until < UNIX_TIMESTAMP(NOW()))')
    connection.commit()

@on_gamemode_init
def on_start():
    set_timer(check_for_unmute, 10000, True)