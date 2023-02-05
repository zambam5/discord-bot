# python3.11
# TODO Need to add ways to handle errors in requests for APIs
# TODO Add slash commands

import discord
from discord.ext.commands import Bot
from discord import Intents
import logging
import datetime
import json
import os.path
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
dt = datetime.datetime.now().strftime("%Y-%m-%d")
handler = logging.FileHandler(
    filename="./logs/discord-" + dt + ".log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


if os.path.isfile("./config/config-test.json"):
    with open("./config/config-test.json", "r") as f:
        config = json.load(f)


twitch = dict()
youtube = dict()

intents = Intents(
    guilds=True,
    members=True,
    presences=True,
    messages=True,
    reactions=False,
    voice_states=True,
    message_content=True,
    emojis_and_stickers=True,
)


class MyBot(Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.reminders")
        # await bot.load_extension("cogs.streamer_role")
        await self.load_extension("cogs.roles")
        await self.load_extension("cogs.wizards_event_posts")
        await self.load_extension("cogs.misc")
        # The following commands require waiting for the bot to be ready
        asyncio.create_task(self.load_extension("cogs.twitch_notif"))
        asyncio.create_task(self.load_extension("cogs.yt_notif"))
        asyncio.create_task(self.load_extension("cogs.ffz_sync"))


bot = MyBot(intents=intents, command_prefix="!", log_handler=None)
# bot.tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="you struggle"
        )
    )
    logger.info("Logged in as " + bot.user.name)

    mchannel = bot.get_channel(422170422516121612)
    await mchannel.send("reboot successful")
    # await bot.tree.sync(guild=discord.Object(id=422170422516121610))
    # await bot.tree.sync(guild=discord.Object(id=504675193751601152))


TOKEN = str(config["DISCORD"]["TOKEN"])
logger.info(TOKEN)
try:
    print("starting bot")
    bot.run(TOKEN)
except:
    logger.exception("message: ")
