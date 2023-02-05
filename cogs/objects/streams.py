import logging, time

logger = logging.getLogger("__main__." + __name__)


class StreamStatus:
    # TODO Figure out how much leg work this class should be doing
    # Answer: as much as possible
    # TODO Add a method for creating the dict needed for twitch config file
    # done
    # It should carry all the relevant info listed in __slots__
    __slots__ = ("ping", "offline", "game", "cd", "status", "cooldown")

    def __init__(self, streamdict: dict) -> None:
        self.status = []
        for item in streamdict.keys():
            setattr(self, item, streamdict[item])
        pass

    def create_dict(self) -> dict:
        """This method generates the dictionary needed in twitch_commands.py to update
        the config file

        Returns:
            dict: Updates the ping, offline, game, and cd items in a json file
        """
        dict_keys = ["ping", "offline", "game", "cd"]
        return {key: getattr(self, key) for key in dict_keys}

    def update_cooldown(self, t: int):
        """Updates the cooldown attribute based on if the stream is online or

        Args:
            status (bool): True if online, False if offline
            t (int): Unix timestamp
        """
        if self.status[0]:
            self.cooldown = t + self.cd["online"]
        else:
            self.cooldown = t + self.cd["offline"]

    def update_stream_status(self, new) -> bool:
        """Updates the self.status attribute based on input

        Args:
            new (list): The updated status of the stream

        Returns:
            bool: Returns False by default, if the cooldown has not been reached, or if self.status = new. Returns True otherwise
        """
        t = time.time()  # time of update
        if self.status == []:
            self.status = new
            self.update_cooldown(t)
        else:
            if t < self.cooldown:
                return False
            elif self.status == new:
                self.update_cooldown(t)
                return False
            else:
                self.status = new
                self.update_cooldown(t)
                return True
        return False

    def update_messages(
        self,
        message_to_update: str,
        message_type: str,
        remove: bool = False,
        add: bool = False,
    ):
        """Either adds or removes a message

        Args:
            message_to_update (str): The message to be updated
            message_type (str): Whether the message is for online, offline, or game change
            remove (bool, optional): If True, a message is being removed. Defaults to None.
            add (bool, optional): If True, a message is being added. Defaults to None.
        """
        # remove or add set to True depending on action
        # message is either the message to remove or the message to add
        valid_message_types = ("ping", "offline", "game")
        if message_type not in valid_message_types:
            raise ValueError(
                f"Expected either 'ping', 'offline', 'game' for message_type, got {message_type} instead"
            )
        if remove:
            type_container = getattr(self, message_type)
            messages = type_container["messages"]
            new_messages = [x for x in messages != messages[message_to_update]]
            type_container["messages"] = new_messages
            setattr(self, message_type, type_container)
        elif add:
            type_container = getattr(self, message_type)
            messages = type_container["messages"].append(message_to_update)
            type_container["messages"] = messages
            setattr(self, message_type, type_container)

    def update_cd(self, message_type: str, amount):
        """Adds a specified amount to the cooldown time of a message type

        Args:
            message_type (str): Offline, online
            amount (str, int): Either a string or an int. Must convert to an int. Amount of time to be added
        """
        try:
            self.cd[message_type] = int(amount)
        except ValueError:
            raise ValueError("The amount must be able to be converted to an int")

    def add_custom_message(
        self, new_message: str, embed: bool, link=None, title=None, url=None
    ):
        """Adds a custom message to be used the next time stream goes

        Args:
            new_message (str): _description_
            embed (bool): True if there is an embed, false if there is not
            link (str, optional): A custom link to be used in an embed. Defaults to None.
            title (str, optional): The title of the embed. Defaults to None.
            url (str, optional): The URL of the image to be used in the embed. Defaults to None.
        """
        self.ping["custom"] = [True]
        x = dict()
        if embed:
            x = dict()
            x["embed"] = True
            x["message"] = new_message
            x["link"] = link
            x["title"] = title
            x["url"] = url
        else:
            x["embed"] = False
            x["message"] = new_message
        self.ping["custom"].append(x)

    def remove_custom_message(self):
        """Removes the previously added custom message"""
        self.ping["custom"] = [False]
