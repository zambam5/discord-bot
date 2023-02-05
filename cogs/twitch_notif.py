import aiohttp, json, datetime, logging, asyncio, time, os, random
from discord.ext import tasks, commands
from cogs.APIs.twitch import TwitchAPI
from cogs.twitch_commands import TwitchCommands
from cogs.twitch_status import TwitchStatus
import discord
from cogs.objects.streams import StreamStatus

logger = logging.getLogger("__main__." + __name__)


class DiscordNotif(TwitchCommands, TwitchStatus):
    # ? Check and see if anything can be made a static method
    # ^ No, all of them require referencing other attributes or methods
    # TODO Work on cooldown management
    # TODO Incorporate a class for handling carrying info for each stream
    """Class to setup discord notification when a stream goes live"""

    def __init__(self, discord):
        """Constructor for the DiscordNotif class

        Args:
            discord (class): Discord client object
        """
        self.discord = discord
        self.configpath = "config/twitch-test.json"
        self.process_config(self.configpath)
        self.live_ping.start()

    def process_config(self, configpath: str):
        # TODO add section to config for server
        if os.path.isfile(configpath):
            # check for existing config file
            with open(configpath, "r") as f:
                r = json.load(f)
            self.ID = r["ID"]
            self.TOKEN = r["TOKEN"]
            self.secret = r["SECRET"]
            self.default = r["DEFAULT_ERROR"]
            self.streams = {}
            for channel in r["NOTIFICATIONS"]:
                self.streams[channel] = StreamStatus(r["NOTIFICATIONS"][channel])
            self.path = r["PATH"]
            self.status = None
        # figure out what to do if no config file
        else:
            with open(configpath, "w"):
                f.write(json.dumps({}))

    async def custom_starting_message(
        self, username, user_info, mention, channel, embedded
    ):
        if embedded:
            message_d = user_info["custom"][1]
            message = mention + " " + message_d["message"]
            title = message_d["title"]
            link = message_d["link"]
            if message_d["url"]:
                embed = discord.Embed(
                    title=title,
                    color=discord.Colour.purple(),
                    url=message_d["url"],
                    description=f"[Click here to watch stream](https://twitch.tv/{username})",
                )
                embed.set_image(url=link)
                await channel.purge(limit=100, check=self.is_me)
                await channel.send(message, embed=embed)
                self.streams[username].remove_custom_message()
                self.update_config(channel)
            else:
                embed = discord.Embed(
                    title=title,
                    color=discord.Colour.purple(),
                    url=f"https://twitch.tv/{username}",
                    description=f"[Click here to watch stream](https://twitch.tv/{username})",
                )
                embed.set_image(url=link)
                await channel.purge(limit=100, check=self.is_me)
                await channel.send(message, embed=embed)
                self.streams[username].remove_custom_message()
                self.update_config(username)
        else:
            message = mention + " " + user_info["custom"][1]["message"]
            await channel.purge(limit=100, check=self.is_me)
            await channel.send(message)
            self.streams[username].remove_custom_message()
            self.update_config(channel)

    async def stream_starting(self, username, game):
        logger.info("Attempting to post message for %s", username)
        user_info = self.streams[username].ping
        # user_info["guild"] = self.streams[username].guild
        ping_channel = user_info["channel"]
        channel = self.discord.get_channel(ping_channel)
        role = user_info["role"]
        if role == user_info["guild"]:
            mention = "@everyone"
        else:
            g = self.discord.get_guild(user_info["guild"])
            mention = g.get_role(role).mention
        if not user_info["custom"][0]:
            ping_list = user_info["messages"]
            message = mention + " " + random.choice(ping_list).format(game)
            await channel.purge(limit=100, check=self.is_me)
            await channel.send(message)
        else:
            embedded = user_info["custom"][1]["embed"]
            await self.custom_starting_message(
                username, user_info, mention, channel, embedded
            )

    async def stream_ended(self, username):
        user_info = self.streams[username].offline
        ping_channel = user_info["channel"]
        ping_list = user_info["messages"]
        if ping_list != False:
            message = random.choice(ping_list)
            channel = self.discord.get_channel(ping_channel)
            await channel.purge(limit=100, check=self.is_me)
            await channel.send(message)
        else:
            channel = self.discord.get_channel(ping_channel)
            await channel.purge(limit=100, check=self.is_me)

    async def game_change(self, username, game):
        user_info = self.streams[username].game
        ping_channel = user_info["channel"]
        message = user_info["messages"].format(game)
        channel = self.discord.get_channel(ping_channel)
        await channel.send(message)

    @tasks.loop(seconds=30)
    async def live_ping(self):
        """
        The function to loop
        """
        # logger.info("starting a loop")
        """if self.status == None:
            await self.get_initial_status()
        usernames = self.notifications.keys()
        current_status = await self.check_live(usernames, self.status)
        self.status = current_status
        logger.info(self.status)"""
        try:
            usernames = self.streams.keys()
            await self.check_live(usernames)
        except:
            logger.exception("Unhandled Exception: ")

    @live_ping.before_loop
    async def before_live_ping(self):
        """
        Instantiate Twitch client
        Delay start of the loop until the bot object gives the ready event
        """
        await self.start_client()
        await self.get_initial_status()
        # logger.info("twitch notifs waiting on bot")
        # await self.discord.wait_until_ready()


async def setup(bot):
    logger.info("Twitch notifs loaded")
    await bot.add_cog(DiscordNotif(bot))
