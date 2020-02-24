class Move:
    """Model for a character's move."""

    def __init__(self, name: str, title: str, image: str):
        """
        Construct move object.

        :param name: `str` code name of the move
        :param title: `str` full name of the move
        :param image: `str` hitbox link
        """
        self.name = name
        self.title = title
        self.image = image
        self.startup = ""
        self.on_shield = ""
        self.active_on = ""
        self.total_frames = ""
        self.landing_lag = ""
        self.base_dmg = ""
        self.shield_lag = ""
        self.shield_stun = ""

    def set_name(self, n: str):
        """
        Set the code name of the move.

        :param n: `str`
        """
        self.name = n

    def set_title(self, t: str):
        """
        Set the full name of the move.

        :param t: `str`
        """
        self.title = t

    def set_image(self, i: str):
        """
        Set the hitbox link of the move.

        :param i: `str`
        """
        self.image = i

    def set_startup(self, s: str):
        """
        Set the start up of the move.

        :param s: `str`
        """
        self.startup = s

    def set_onshield(self, s: str):
        """
        Set the on shield advantage of the move.

        :param s: `str`
        """
        self.on_shield = s

    def set_activeon(self, a: str):
        """
        Set the active frames of the move.

        :param a: `str`
        """
        self.active_on = a

    def set_totalframes(self, t: str):
        """
        Set the total frames of the move.

        :param t: `str`
        """
        self.total_frames = t

    def set_landinglag(self, l: str):
        """
        Set the landing lag of the move.

        :param l: `str`
        """
        self.landing_lag = l

    def set_basedmg(self, d: str):
        """
        Set the damage of the move.

        :param d: `str`
        """
        self.base_dmg = d

    def set_shieldlag(self, l: str):
        """
        Set the shield lag of the move.

        :param l: `str`
        """
        self.shield_lag = l

    def set_shieldstun(self, s: str):
        """
        Set the shield stun of the move.

        :param s: `str`
        """
        self.shield_stun = s

    def get_name(self) -> str:
        """
        Get the code name of the move.

        :return: `str`
        """
        return self.name

    def get_title(self) -> str:
        """
        Get the title of the move.

        :return: `str`
        """
        return self.title

    def get_image(self) -> str:
        """
        Get the hitbox link of the move.

        :return: `str`
        """
        return self.image

    def get_startup(self) -> str:
        """
        Get the start up frames of the move.

        :return: `str`
        """
        return self.startup

    def get_onshield(self) -> str:
        """
        Get the on shield advantage of the move.

        :return: `str`
        """
        return self.on_shield

    def get_activeon(self) -> str:
        """
        Get the active frames of the move.

        :return: `str`
        """
        return self.active_on

    def get_totalframes(self) -> str:
        """
        Get the total frames of the move.

        :return: `str`
        """
        return self.total_frames

    def get_landinglag(self) -> str:
        """
        Get the landing lag of the move.

        :return: `str`
        """
        return self.landing_lag

    def get_basedmg(self) -> str:
        """
        Get the damage of the move.

        :return: `str`
        """
        return self.base_dmg

    def get_shieldlag(self) -> str:
        """
        Get the shield lag of the move.

        :return: `str`
        """
        return self.shield_lag

    def get_shieldstun(self) -> str:
        """
        Get the shield stun of the move.

        :return: `str`
        """
        return self.shield_stun

    def get_frame_data(self) -> dict:
        """
        Get a list of all the frame data.

        :return: `str`
        """
        return {
            "startup": self.startup,
            "onshield": self.on_shield,
            "activeon": self.active_on,
            "totalframes": self.total_frames,
            "landinglag": self.landing_lag,
            "basedmg": self.base_dmg,
            "shieldlag": self.shield_lag,
            "shieldstun": self.shield_stun
        }
