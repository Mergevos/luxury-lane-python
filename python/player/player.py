from pysamp.player import Player as BasePlayer
from functools import wraps

MESSAGE_ERROR = 1
MESSAGE_WARNING = 2
MESSAGE_USAGE = 3
MESSAGE_HELP = 4
MESSAGE_SUCCESS = 5 
MESSAGE_ANNOUNCEMENT = 6
MESSAGE_DEBUG = 7

class Player(BasePlayer):
    _pool: dict[int, BasePlayer] = {}

    account = None
    role = None 

    def __init__(self, player_id):
        super().__init__(player_id)
        self.account = None
        self.role = None

    def message_send(self, message_level: int, text: str) -> bool:
        _info = None
        _color = None

        if not self.is_connected():
            return False

        if message_level == MESSAGE_ERROR:
            _info = '>> Error: ' 
            _color = 0xFC2C03FF
        
        elif message_level == MESSAGE_USAGE:
            _info = '>> Usage: ' 
            _color = 0xFC9003FF

        elif message_level == MESSAGE_WARNING:
            _info = '>> Waning: ' 
            _color = 0xFCE803FF

        elif message_level == MESSAGE_HELP:
            _info = '>> Help: ' 
            _color = 0x75231DFF

        elif message_level == MESSAGE_SUCCESS:
            _info = '>> Success: ' 
            _color = 0xA1FC03FF

        elif message_level == MESSAGE_ANNOUNCEMENT:
            _info = '>> Announcement: ' 
            _color = 0x688C8AFF

        elif message_level == MESSAGE_DEBUG:
            _info = '>> Debug: ' 
            _color = 0x326376FF
        
        self.send_client_message(_color, f'{_info}{text}')
        return True

    
    @classmethod
    def from_pool(cls: BasePlayer, player) -> BasePlayer:
        if isinstance(player, int):
            player_id = player
        
        if isinstance(player, BasePlayer):
            player_id = player.id

        player: Player = cls._pool.get(player_id)

        if not player:
            cls._pool[player_id] = player = cls(player_id)

        return player

    @classmethod
    def remove_from_pool(cls, player: BasePlayer):
        del cls._pool[player.id]
    
    @classmethod
    def using_pool(cls, func):
        @wraps(func)
        def from_pool(*args, **kwargs):
            args = list(args)
            args[0] = cls.from_pool(args[0])
            return func(*args, **kwargs)

        return from_pool

@Player.on_disconnect
@Player.using_pool
def on_player_disconnect(player: Player, reason: int):
    player.remove_from_pool(player)

# Messages

