from ast import alias
import aiohttp, json, datetime, logging, asyncio, time, os, random
from discord.ext import tasks, commands
from setuptools import Command
from cogs.APIs.twitch import TwitchAPI
from cogs.twitch_commands import TwitchCommands
import discord

logger = logging.getLogger("__main__." + __name__)


class DiscordNotif(TwitchCommands):
    # ? Check and see if anything can be made a static method
    """Class to setup discord notification when a stream goes live"""

    def __init__(self, discord):
        """Constructor for the DiscordNotif class

        Args:
            discord (class): Discord client object
            ID (str): Twitch API ID
            token (str): OAuth token corresponding to the ID for the Twitch API
        """
        self.discord = discord
        self.configpath = "config/twitch.json"
        self.process_config(self.configpath)
        self.live_ping.start()

    async def start_client(self):
        """Instantiate the TwitchAPI class

        Sets class attribute for client
        """
        self.client = await TwitchAPI.create(self.ID, self.secret, self.path)

    async def get_initial_status(self):
        """Get first status of each stream
        Setup initial cooldowns
        TODO test
        """
        # TODO test
        usernames = self.notifications.keys()
        response = await self.client.get_status(usernames)
        self.status = await self.process_response(response, usernames)
        self.cds = {}
        for username in usernames:
            cds = self.notifications[username]["cd"]
            if self.status[username][0]:
                self.cds[username] = time.time() + cds["online"]
            else:
                self.cds[username] = time.time() + cds["offline"]

    async def process_response(self, response: list, usernames: list):
        status = {}
        if response == []:
            for username in usernames:
                status[username] = [False]
        elif response == ["expired"]:
            # tell it to go again
            new_check = await self.client.get_status(usernames)
            return await self.process_response(new_check, usernames)
            # ? why not status = await self.process_response(new_check, usernames)
        else:
            for item in response:
                username = item["user_login"]
                gameid = item["game_id"]
                if gameid == "":
                    game = "Unlisted"
                else:
                    game = item["game_name"]
                status[username] = [True, game]
            not_live = [i for i in usernames if i not in status]
            for username in not_live:
                status[username] = [False]
        return status

    async def stream_starting(self, username, game):
        logger.info("Attempting to post message for %s", username)
        user_info = self.notifications[username]["ping"]
        ping_channel = user_info["channel"]
        channel = self.discord.get_channel(id=ping_channel)
        role = user_info["role"]
        if role == user_info["guild"]:
            mention = "@everyone"
        else:
            g = self.discord.get_guild(id=user_info["guild"])
            mention = g.get_role(role_id=role).mention
        if not user_info["custom"][0]:
            ping_list = user_info["messages"]
            message = mention + " " + random.choice(ping_list).format(game)
            await channel.purge(limit=100, check=self.is_me)
            await channel.send(message)
        elif user_info["custom"][1]["embed"]:
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
                self.notifications[username]["ping"]["custom"] = [False]
                self.update_config()
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
                self.notifications[username]["ping"]["custom"] = [False]
                self.update_config()
        else:
            message = mention + " " + user_info["custom"][1]["message"]
            await channel.purge(limit=100, check=self.is_me)
            await channel.send(message)
            self.notifications[username]["ping"]["custom"] = [False]
            self.update_config()

    async def stream_ended(self, username):
        user_info = self.notifications[username]["offline"]
        ping_channel = user_info["channel"]
        ping_list = user_info["messages"]
        if ping_list != False:
            message = random.choice(ping_list)
            channel = self.discord.get_channel(id=ping_channel)
            await channel.purge(limit=100, check=self.is_me)
            await channel.send(message)
        else:
            channel = self.discord.get_channel(id=ping_channel)
            await channel.purge(limit=100, check=self.is_me)

    async def game_change(self, username, game):
        user_info = self.notifications[username]["game"]
        ping_channel = user_info["channel"]
        message = user_info["messages"].format(game)
        channel = self.discord.get_channel(id=ping_channel)
        await channel.send(message)

    async def check_live(self, usernames, last_check):
        """Check the stream status

        Args:
            streamid (str): Name of the stream
            last_check (dict): Most recent status of each stream

        Returns:
            list: Current status of the stream
        """
        currentDT = str(datetime.datetime.now())
        try:
            response = await self.client.get_status(usernames)
            new_check = await self.process_response(response, usernames)
        except:
            logger.exception("message: ")
            return last_check, "error"

        if new_check == last_check:
            usernames_str = ", ".join(usernames)
            logger.info("%s no status change as of %s", usernames_str, currentDT)
            return new_check
        else:
            for username in usernames:
                if last_check[username] == new_check[username]:
                    continue
                elif time.time() < self.cds[username]:
                    # not enough time passed since last check
                    continue
                else:
                    cds = self.notifications[username]["cd"]
                    if not last_check[username][0]:
                        game = new_check[username][1]
                        logger.info("%s live at %s", username, currentDT)
                        await self.stream_starting(username, game)
                        self.cds[username] = time.time() + cds["online"]
                        last_check[username] = new_check[username]
                    elif not new_check[username][0]:
                        logger.info("%s offline at %s", username, currentDT)
                        await self.stream_ended(username)
                        self.cds[username] = time.time() + cds["offline"]
                        last_check[username] = new_check[username]
                    else:
                        game = new_check[username][1]
                        logger.info("%s game change at %s", username, currentDT)
                        await self.game_change(username, game)
                        self.cds[username] = time.time() + cds["online"]
                        last_check[username] = new_check[username]
        return last_check

    @tasks.loop(seconds=60)
    async def live_ping(self):
        """
        The function to loop
        """
        logger.info("starting a loop")
        if self.status == None:
            await self.get_initial_status()
        usernames = self.notifications.keys()
        current_status = await self.check_live(usernames, self.status)
        self.status = current_status
        logger.info(self.status)

    @live_ping.before_loop
    async def before_live_ping(self):
        """
        Instantiate Twitch client
        Delay start of the loop until the bot object gives the ready event
        """
        await self.start_client()
        # await self.get_initial_status()
        logger.info("twitch notifs waiting on bot")
        await self.discord.wait_until_ready()


def setup(bot):
    logger.info("Twitch notifs loaded")
    bot.add_cog(DiscordNotif(bot))
