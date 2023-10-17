import samp
from python.account.account import Account
from pysamp import set_timer, on_gamemode_init
from python.database import Database


def check_for_unmute():
    """
    Unmute players whose mute duration has expired.

    This function checks the database for players who are muted and have reached or exceeded their mute duration.
    It deletes the mute records for these players, effectively unmuting them.

    :return: None
    """

    # Obtain the database connection
    connection = Database.get_connection()
    cursor = Database.get_cursor()

    # Delete mute records for players with expired mute durations
    cursor.execute('DELETE FROM account_muted WHERE account_mute_until IN (SELECT account_mute_until FROM account_muted WHERE account_mute_until < UNIX_TIMESTAMP(NOW()))')
    
    # Delete mute records for players with expired mute durations
    connection.commit()

@on_gamemode_init
def on_start():
    """
    Initialize and start game-related functionality.

    This function is called when the game mode is initialized. It sets a timer to periodically check for expired mutes
    and unmute players.

    :return: None
    """
    # Set a timer to call check_for_unmute every 10 seconds
    set_timer(check_for_unmute, 10000, True)