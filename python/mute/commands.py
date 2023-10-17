from pysamp.player import is_player_connected
from python.player.player import Player, MESSAGE_ERROR, MESSAGE_ANNOUNCEMENT, MESSAGE_SUCCESS
from python.player.permissions import Role, roles
from python.player.commands import has_permission, SERBIAN_ERROR
from python.account.account import Account
from python.database import Database
import time

@Player.command(requires=(has_permission('can_mute'), ), error_message=SERBIAN_ERROR)
@Player.using_pool
def mute(player: Player, target: int, until: int=0, option: int=-1):

    """
    Mute a player.

    :param player: The player performing the mute.
    :param target: The target player's ID.
    :param until: The duration of the mute (default is 0 for permanent).
    :param option: The mute option (-1: forever, 0: hours, 1: days, 2: months).
    :return: 0 if the mute was successful.
    """

    # Obtain target instance
    target_instance = Player.from_pool(int(target))

    # Check if target is connected
    if not target_instance.is_connected():
        return player.message_send(MESSAGE_ERROR, 'Igrac nije konektovan')

    # Check if target is muted
    if target_instance.account.mute:
        return player.message_send(MESSAGE_ERROR, 'Igrac je vec mutiran')

    # Check if until is invalid input
    if int(until) < 0:
        return player.message_send(MESSAGE_ERROR, 'Ne mozes uneti negativan broj')

    # until is valid
    elif int(until) >= 0:
        
        # Check for invalid option
        if int(option) not in (-1, 0, 1, 2):
            return player.message_send(MESSAGE_ERROR, 'Neispravna opcija.\nBez opcije - zauvek\n0 - sati\n1 - dani\n2 - meseci')

        # Sets the target muted and send the message to it and performer
        target_instance.account.mute = True
        target_instance.message_send(MESSAGE_ANNOUNCEMENT, 'Admin vas je mutirao. Ne mozete koristiti komande ni chat.')
        player.message_send(MESSAGE_SUCCESS, f'Uspesno ste mutirali igraca {target_instance.get_name()}')


        if int(option) == -1: # Forever
            target_instance.account.muted_until = 0

        elif int(option) == 0: # hours
            # Sets the muted time and send message to muted and performer
            target_instance.account.muted_until = time.time() + (int(until) * 3600)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} sat(a/i).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} sat(a/i).')
        
        elif int(option) == 1: # Days
            # Sets the muted time and send message to muted and performer
            target_instance.account.muted_until = time.time() + (int(until) * 86400)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} dan(a).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} dan(a)')
        
        elif int(option) == 2: # Months
            # Sets the muted time and send message to muted and performer
            target_instance.account.muted_until = time.time() + (int(until) * 30 * 86400)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} mesec(a).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} mesec(a)')

        # Obtain the database connection
        connection = Database.get_connection()
        cursor = Database.get_cursor()
        
        # Insert data into table and commit
        cursor.execute('INSERT INTO account_muted (account_mute_id, account_mute_until) VALUES (%s, %s)', (target_instance.account.sqlid, target_instance.account.muted_until, ))
        connection.commit()

    # Return 0 to indicate a successful unmute operation

    return 0

@Player.command(requires=(has_permission('can_mute'), ), error_message=SERBIAN_ERROR)
@Player.using_pool
def unmute(player: Player, target: int):
    """
    Unmute a player.

    :param player: The player performing the unmute.
    :param target: The ID of the player to be unmuted.
    :return: 0 if the unmute was successful.
    """
    # Get the target player instance
    target_instance = Player.from_pool(int(target))

    # Check if the target player is connected
    if not target_instance.is_connected():
        return player.message_send(MESSAGE_ERROR, 'Igrac nije konektovan')

    # Check if the target player is muted
    if not target_instance.account.mute:
        return player.message_send(MESSAGE_ERROR, 'Igrac nije mutiran')

    # Unmute the player
    target_instance.account.mute = False
    target_instance.account.muted_until = None

    # Get a database connection and cursor
    connection = Database.get_connection()
    cursor = Database.get_cursor()

    # Delete the mute record for the target player
    cursor.execute('DELETE FROM account_muted WHERE account_mute_id = %s', (target_instance.account.sqlid, ))

    # Commit the database changes
    connection.commit()

    # Send a success message to the administrator
    player.message_send(MESSAGE_SUCCESS, f'Uspesno ste unmutirali igraca {target_instance.get_name()}.')

    # Send an announcement message to the unmuted player
    target_instance.message_send(MESSAGE_ANNOUNCEMENT, 'Admin vas je unmutirao.')

    # Return 0 to indicate a successful unmute operation
    return 0

