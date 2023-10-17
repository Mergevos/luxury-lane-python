import samp
from pysamp import *
import python.database
import python.player
import python.account
import python.mute
import pysamp.callbacks as callbacks


def OnGameModeInit():
    print('Initialized gamemode from PySAMP.')

callbacks.hook()