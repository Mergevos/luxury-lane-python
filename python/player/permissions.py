class Role:
    
    name = None
    can_access_server_settings = None
    def __init__(self, name: str, can_kick: bool=False, can_mute: bool=False, can_ban: bool=False, can_access_server_settings: bool=False):
        self.name = name
        self.class_roles = {
            'can_kick' : can_kick,
            'can_mute' : can_mute,
            'can_ban' : can_ban,
            'can_access_server_settings' : can_access_server_settings
        }

roles = {
    'admin' : Role('admin', can_kick=True, can_mute=True)
}

