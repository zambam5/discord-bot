import json
from discord import Embed, Colour
from datetime import datetime


class EmbedJson:
    def __init__(self, embed: dict) -> None:
        self.dict = embed

    @staticmethod
    def field_value(field):
        if field["value"]:
            return field["value"]
        else:
            return "\u200b"

    @staticmethod
    def timestamp(dt):
        if dt:
            return str(datetime.now())
        else:
            return None

    def update_field(self, index, value):
        field = self.dict["fields"][index]
        field["value"] = value
        self.dict["fields"][index] = field

    def generate_embed(self) -> Embed:
        embed_d = self.dict
        if "timestamp" in self.dict.keys():
            embed_d["timestamp"] = self.timestamp(True)
        for i in range(0, len(self.dict["fields"])):
            field = self.dict["fields"][i]
            embed_d["fields"][i]["value"] = self.field_value(field)
        embed = Embed.from_dict(embed_d)
        return embed
