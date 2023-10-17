import samp
from python.account.account import Account
from pysamp import set_timer, on_gamemode_init
from python.database import Database
import pysamp.callbacks as callbacks


def check_for_unmute():
    
    print('Called')
    connection = Database.get_connection()
    cursor = Database.get_cursor()
    cursor.execute('DELETE FROM account_muted WHERE account_mute_until IN (SELECT account_mute_until FROM account_muted WHERE account_mute_until < UNIX_TIMESTAMP(NOW()))')
    connection.commit()

def OnGameModeInit():
    print('ej')
    set_timer(check_for_unmute, 10000, True)
    return 1


callbacks.hook()