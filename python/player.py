from pysamp.player import Player as BasePlayer
from functools import wraps


class Player(BasePlayer):
    _pool: dict[int, BasePlayer] = {}

    _account = None

    def __init__(self, player_id):
        super().__init__(player_id)

    def set_account(self, account):
        self._account = account

    def get_account(self) -> int:
        return self._account

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