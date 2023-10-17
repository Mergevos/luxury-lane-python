import samp
from pysamp import *
import python.database
import python.player
import python.account
import python.mute

@on_gamemode_init
def on_start():
    print('Initialized gamemode from PySAMP.')
