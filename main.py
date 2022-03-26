import discord
from discord.ext.commands import Bot
from discord import Intents
import logging
import datetime
import json
import os.path

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


if os.path.isfile("./config/config.json"):
    with open("./config/config.json", "r") as f:
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
)
bot = Bot(intents=intents, command_prefix="!")
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


bot.load_extension("cogs.reminders")
# bot.load_extension("cogs.streamer_role")
bot.load_extension("cogs.misc")
bot.load_extension("cogs.twitch_notif")
bot.load_extension("cogs.yt_notif")


TOKEN = str(config["DISCORD"]["TOKEN"])
logger.info(TOKEN)
try:
    print("starting bot")
    bot.run(TOKEN)
except:
    logger.exception("message: ")
