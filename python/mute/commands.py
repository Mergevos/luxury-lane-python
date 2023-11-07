from pysamp.player import is_player_connected
from python.player.player import Player, MESSAGE_ERROR, MESSAGE_ANNOUNCEMENT, MESSAGE_SUCCESS, get_player_from_name
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
    try:
        target = int(target)
    except ValueError:
        return player.message_send(MESSAGE_ERROR, 'Igrac treba biti broj')
    
    try:
        until = int(until)
    except ValueError:
        return player.message_send(MESSAGE_ERROR, 'Rok do kada treba biti broj')

    try:
        option = int(option)
    except ValueError:
        return player.message_send(MESSAGE_ERROR, 'Opcija treba biti broj')

    target_instance = Player.from_pool(int(target))
    
    if not target_instance.is_connected():
        return player.message_send(MESSAGE_ERROR, 'Igrac nije konektovan')

    if target_instance.account.mute:
        return player.message_send(MESSAGE_ERROR, 'Igrac je vec mutiran')

    if until < 0:
        return player.message_send(MESSAGE_ERROR, 'Ne mozes uneti negativan broj')

    elif until >= 0:
        
        if option not in (-1, 0, 1, 2):
            return player.message_send(MESSAGE_ERROR, 'Neispravna opcija.\nBez opcije - zauvek\n0 - sati\n1 - dani\n2 - meseci')

        target_instance.account.mute = True
        target_instance.message_send(MESSAGE_ANNOUNCEMENT, 'Admin vas je mutirao. Ne mozete koristiti komande ni chat.')
        player.message_send(MESSAGE_SUCCESS, f'Uspesno ste mutirali igraca {target_instance.get_name()}')


        if option == -1: # Forever
            target_instance.account.muted_until = 0

        elif option == 0: # hours
            target_instance.account.muted_until = time.time() + (int(until) * 3600)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} sat(a/i).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} sat(a/i).')
        
        elif option == 1: # Days
            target_instance.account.muted_until = time.time() + (int(until) * 86400)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} dan(a).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} dan(a)')
        
        elif option == 2: # Months
            target_instance.account.muted_until = time.time() + (int(until) * 30 * 86400)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} mesec(a).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} mesec(a)')

        connection = Database.connection
        cursor = connection.cursor()
        
        cursor.execute('INSERT INTO account_muted (account_mute_id, account_mute_until) VALUES (%s, %s)', (target_instance.account.sqlid, target_instance.account.muted_until, ))
        connection.commit()

    return 0

@Player.command(requires=(has_permission('can_mute'), ), error_message=SERBIAN_ERROR)
@Player.using_pool
def offlinemute(player: Player, target: str, until: int=0, option: int=-1):

    """
    Mute a player offline.

    :param player: The player performing the mute.
    :param target: The target player's ID.
    :param until: The duration of the mute (default is 0 for permanent).
    :param option: The mute option (-1: forever, 0: hours, 1: days, 2: months).
    :return: 0 if the mute was successful.
    """
    
    try:
        until = int(until)
    except ValueError:
        return player.message_send(MESSAGE_ERROR, 'Rok do kada treba biti broj')

    try:
        option = int(option)
    except ValueError:
        return player.message_send(MESSAGE_ERROR, 'Opcija treba biti broj')

    target_instance = get_player_from_name(target)
    
    if target_instance is not None:
        return player.message_send(MESSAGE_ERROR, 'Igrac je konektovan, koristite /mute komandu')

    connection = Database.connection
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM account LEFT JOIN account_muted ON account.account_id = account_muted.account_mute_id WHERE account.account_name = %s", (target,))
    row = cursor.fetchone()
    if row is None:
        return player.message_send(MESSAGE_ERROR, 'Igrac ne postoji')
    else:
        target_mute_until = None
        target_id = None
        if row['account_mute_id'] is not None:
            return player.message_send(MESSAGE_ERROR, 'Igrac je vec mutiran')

        target_id = row['account_id']

        if until < 0:
            return player.message_send(MESSAGE_ERROR, 'Ne mozes uneti negativan broj')

        elif until >= 0:
            
            if option not in (-1, 0, 1, 2):
                return player.message_send(MESSAGE_ERROR, 'Neispravna opcija.\nBez opcije - zauvek\n0 - sati\n1 - dani\n2 - meseci')

            player.message_send(MESSAGE_SUCCESS, f'Uspesno ste mutirali igraca {target}')


            if option == -1: # Forever
                target_mute_until = 0

            elif option == 0: # hours
                target_mute_until = time.time() + (int(until) * 3600)
                player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} sat(a/i).')
            
            elif option == 1: # Days
                target_mute_until = time.time() + (int(until) * 86400)
                player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} dan(a)')
            
            elif option == 2: # Months
                target_mute_until = time.time() + (int(until) * 30 * 86400)
                player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} mesec(a)')
            
            cursor.execute('INSERT INTO account_muted (account_mute_id, account_mute_until) VALUES (%s, %s)', (target_id, target_mute_until, ))
            connection.commit()

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
    target_instance = Player.from_pool(int(target))

    if not target_instance.is_connected():
        return player.message_send(MESSAGE_ERROR, 'Igrac nije konektovan')

    if not target_instance.account.mute:
        return player.message_send(MESSAGE_ERROR, 'Igrac nije mutiran')

    # Unmute the player
    target_instance.account.mute = False
    target_instance.account.muted_until = None

    connection = Database.connection
    cursor = connection.cursor()

    cursor.execute('DELETE FROM account_muted WHERE account_mute_id = %s', (target_instance.account.sqlid, ))
    connection.commit()

    player.message_send(MESSAGE_SUCCESS, f'Uspesno ste unmutirali igraca {target_instance.get_name()}.')

    target_instance.message_send(MESSAGE_ANNOUNCEMENT, 'Admin vas je unmutirao.')

    return 0

