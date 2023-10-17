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


    target_instance = Player.from_pool(int(target))

    if not target_instance.is_connected():
        return player.message_send(MESSAGE_ERROR, 'Igrac nije konektovan')

    if target_instance.account.mute:
        return player.message_send(MESSAGE_ERROR, 'Igrac je vec mutiran')

    if int(until) < 0:
        return player.message_send(MESSAGE_ERROR, 'Ne mozes uneti negativan broj')

    elif int(until) >= 0:
        
        if int(option) not in (-1, 0, 1, 2):
            return player.message_send(MESSAGE_ERROR, 'Neispravna opcija.\nBez opcije - zauvek\n0 - sati\n1 - dani\n2 - meseci')

        target_instance.account.mute = True
        target_instance.message_send(MESSAGE_ANNOUNCEMENT, 'Admin vas je mutirao. Ne mozete koristiti komande ni chat.')
        player.message_send(MESSAGE_SUCCESS, f'Uspesno ste mutirali igraca {target_instance.get_name()}')

        if int(option) == -1: # Forever
            target_instance.account.muted_until = 0

        elif int(option) == 0: # hours
            target_instance.account.muted_until = time.time() + (int(until) * 3600)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} sat(a/i).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} sat(a/i).')
        
        elif int(option) == 1: # Days
            target_instance.account.muted_until = time.time() + (int(until) * 86400)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} dan(a).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} dan(a)')
        
        elif int(option) == 2: # Months
            target_instance.account.muted_until = time.time() + (int(until) * 30 * 86400)
            target_instance.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirani ste na {until} mesec(a).')
            player.message_send(MESSAGE_ANNOUNCEMENT, f'Mutirali ste ga na {until} mesec(a)')
        
        connection = Database.get_connection()
        cursor = Database.get_cursor()
        cursor.execute('INSERT INTO account_muted (account_mute_id, account_mute_until) VALUES (%s, %s)', (target_instance.account.sqlid, target_instance.account.muted_until, ))
        connection.commit()

        
    return 0

@Player.command(requires=(has_permission('can_mute'), ), error_message=SERBIAN_ERROR)
@Player.using_pool
def unmute(player: Player, target: int):
    target_instance = Player.from_pool(int(target))

    if not target_instance.is_connected():
        return player.message_send(MESSAGE_ERROR, 'Igrac nije konektovan')

    if not target_instance.account.mute:
        return player.message_send(MESSAGE_ERROR, 'Igrac nije mutiran')

    target_instance.account.mute = False
    target_instance.account.muted_until = None

    connection = Database.get_connection()
    cursor = Database.get_cursor()
    cursor.execute('DELETE FROM account_muted WHERE account_mute_id = %s', (target_instance.account.sqlid, ))
    connection.commit()

    player.message_send(MESSAGE_SUCCESS, f'Uspesno ste unmutirali igraca {target_instance.get_name()}.')
    target_instance.message_send(MESSAGE_ANNOUNCEMENT, 'Admin vas je unmutirao.')
    return 0

