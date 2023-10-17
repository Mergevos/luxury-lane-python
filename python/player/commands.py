from python.player.player import Player, MESSAGE_SUCCESS, MESSAGE_ERROR
from python.player.permissions import Role, roles
from pysamp.commands import BaseMessage

SERBIAN_ERROR = BaseMessage(
    text='Niste ovlasceni.',
    color=0xFF0000FF,
)

@Player.using_pool
def player_has_permission(player: Player, role_key: str):
    if not player.role:
        return False
    return player.role.class_roles.get(role_key)

def has_permission(role: str):
    return lambda playerid: player_has_permission(playerid, role)

@Player.command(error_message=SERBIAN_ERROR)
@Player.using_pool
def assign(player: Player, params: str):
    
    if params in roles:

        if player.role == roles[params]:
            return player.message_send(MESSAGE_ERROR, "HEJJJ")

    else:
        return player.message_send(MESSAGE_ERROR, 'Invalid')

    for role_key in roles:
        if role_key == params:
            player.role = roles[role_key]
            player.message_send(MESSAGE_SUCCESS, f'Player role is now {player.role} and instance was {roles[params]}')
            break
        else:
            player.message_send(MESSAGE_ERROR, 'Invalid role')
