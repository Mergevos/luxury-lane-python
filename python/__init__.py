from pysamp import *
import python.database
import python.player.permissions
import python.player.player
import python.account.account


@on_gamemode_init
def on_start():
    print('Initialized gamemode from PySAMP.')
    return 1