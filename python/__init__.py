from pysamp import *
import python.database
import python.player
import python.account


@on_gamemode_init
def on_start():
    print('Initialized gamemode from PySAMP.')