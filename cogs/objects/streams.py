import logging, time

logger = logging.getLogger("__main__." + __name__)


class StreamStatus:
    # TODO Figure out how much leg work this class should be doing
    # Answer: as much as possible
    # TODO Add a method for creating the dict needed for twitch config file
    # done
    # It should carry all the relevant info listed in __slots__
    __slots__ = ("ping", "offline", "game", "cd", "guild", "status", "cooldown")

    def __init__(self, streamdict: dict) -> None:
        self.status = []
        self.process_dict(streamdict)
        pass

    def process_dict(self, streamdict: dict):
        for item in streamdict.keys():
            setattr(self, item, streamdict[item])

    def create_dict(self):
        dict_keys = ["ping", "offline", "game", "cd", "guild"]
        d = dict()
        for item in dict_keys:
            d[item] = getattr(self, item)
        return d

    def update_cooldown(self, status: bool, t):
        if status:
            self.cooldown = t + self.cd["online"]
            logger.info("Online cooldown")
        else:
            self.cooldown = t + self.cd["offline"]
            logger.info("Offline cooldown")

    def update_status(self, new):
        # Return False for no change
        # Return True for change
        t = time.time()  # time of update
        if self.status == []:
            self.status = new
            self.update_cooldown(new[0], t)
        else:
            if t < self.cooldown:
                return False
            elif self.status == new:
                self.update_cooldown(new[0], t)
                return False
            else:
                self.status = new
                self.update_cooldown(new[0], t)
                return True
        return False

    def update_messages(self, message: str, message_type: str, remove=None, add=None):
        # remove or add set to True depending on action
        # message is either the message to remove or the message to add
        if remove:
            type_container = getattr(self, message_type)
            messages = type_container["messages"]
            new_messages = [x for x in messages != messages[message]]
            type_container["messages"] = new_messages
            setattr(self, message_type, type_container)
        elif add:
            type_container = getattr(self, message_type)
            messages = type_container["messages"].append(message)
            type_container["messages"] = messages
            setattr(self, message_type, type_container)

    def update_cd(self, message_type, amount):
        self.cd[message_type] = int(amount)

    def add_custom_message(self, message, embed: bool, link=None, title=None, url=None):
        self.ping["custom"] = [True]
        x = dict()
        if embed:
            x = dict()
            x["embed"] = True
            x["message"] = message
            x["link"] = link
            x["title"] = title
            x["url"] = url
        else:
            x["embed"] = False
            x["message"] = message
        self.ping["custom"].append(x)

    def remove_custom_message(self):
        self.ping["custom"] = [False]
