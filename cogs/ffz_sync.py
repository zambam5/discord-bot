import aiohttp, json, datetime, logging, asyncio, time, os
from discord.ext import tasks, commands
import discord

from cogs.objects.ffz_emote import Emote

logger = logging.getLogger("__main__." + __name__)


class FFZSync(commands.Cog):
    def __init__(self, bot, config: dict):
        self.bot = bot
        self.config = config
        self.sync_task.start()

    @staticmethod
    async def ffz_api(channel):
        url = f"https://api.frankerfacez.com/v1/room/{channel}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                response = await res.json()
                emoteset = str(response["room"]["set"])
                emotes = response["sets"][emoteset]["emoticons"]
                await session.close()
        return emotes

    @staticmethod
    def process_list(emotelist):
        x = []
        for item in emotelist:
            emote = Emote(item)
            if emote.is_wide:
                # we cannot upload the wide emotes to discord
                continue
            else:
                x.append(emote)
        return x

    @staticmethod
    async def process_guild(guild):
        x = {}
        emojis = await guild.fetch_emojis()
        for item in emojis:
            x[item.name] = item.id
        return x

    @staticmethod
    def compare_lists(emotelist, guilddict):
        x = []
        for item in emotelist:
            if item.name in guilddict.keys():
                # skip the ones already in the server
                continue
            else:
                x.append(item)
        return x

    async def process_diff(self, diff, guild):
        for item in diff:
            try:
                emote_im = await item.load_image("4")
            except KeyError:
                try:
                    emote_im = await item.load_image("2")
                except KeyError:
                    emote_im = await item.load_image("1")
            name = item.name
            await guild.create_custom_emoji(name=name, image=emote_im)

    @tasks.loop(seconds=600)
    async def sync_task(self):
        for item in self.config.keys():
            emotes = await self.ffz_api(item)
            emote_list = self.process_list(emotes)
            guild = self.bot.get_guild(id=self.config[item])
            guild_dict = await self.process_guild(guild)
            diff = self.compare_lists(emote_list, guild_dict)
            await self.process_diff(diff, guild)

    @sync_task.before_loop
    async def before_sync_task(self):
        logger.info("FFZ Sync waiting on bot")
        await self.bot.wait_until_ready()


if os.path.isfile("./config/ffz.json"):
    with open("./config/ffz.json", "r") as f:
        config = json.load(f)


def setup(bot):
    logger.info("Twitch notifs loaded")
    bot.add_cog(FFZSync(bot, config))
