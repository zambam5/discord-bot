import aiohttp, json, datetime, logging, asyncio, time, os, random
from discord.ext import tasks, commands
from setuptools import Command
import discord
from cogs.APIs.twitch import TwitchAPI

logger = logging.getLogger("__main__." + __name__)


class TwitchStatus:
    async def start_client(self):
        """Instantiate the TwitchAPI class

        Sets class attribute for client
        """
        self.client = await TwitchAPI.create(self.ID, self.secret, self.path)

    async def get_initial_status(self):
        """Get first status of each stream
        Setup initial cooldowns
        """
        usernames = self.streams.keys()
        response = await self.client.get_status(usernames)
        status = await self.process_response(response, usernames)
        for username in usernames:
            self.streams[username].update_stream_status(status[username])

    async def process_response(self, response: list, usernames: list):
        status = {}
        if response == []:
            for username in usernames:
                status[username] = [False]
        elif response == ["expired"]:
            # tell it to go again
            new_check = await self.client.get_status(usernames)
            # return await self.process_response(new_check, usernames)
            status = await self.process_response(new_check, usernames)
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

    async def check_live(self, usernames):
        # TODO Find a better way to detect game change
        """Check the stream status

        Args:
            streamid (str): Name of the stream

        Returns:
            list: Current status of the stream
        """
        currentDT = str(datetime.datetime.now())
        log_message = f"{currentDT}: "
        try:
            response = await self.client.get_status(usernames)
            new_check = await self.process_response(response, usernames)
            print(new_check)
        except aiohttp.ClientOSError:
            logger.exception("message: ")
            return
        for username in usernames:
            if self.streams[username].status[0]:
                g = self.streams[username].status[1]
            else:
                g = True
            change = self.streams[username].update_stream_status(new_check[username])
            if change:
                if self.streams[username].status[0] and g == True:
                    game = new_check[username][1]
                    # logger.info("%s live at %s", username, currentDT)
                    log_message += f"{username} changed to live. "
                    await self.stream_starting(username, game)
                elif not self.streams[username].status[0]:
                    # logger.info("%s offline at %s", username, currentDT)
                    log_message += f"{username} changed to offline. "
                    await self.stream_ended(username)
                else:
                    game = new_check[username][1]
                    # logger.info("%s game change at %s", username, currentDT)
                    log_message += f"{username} changed game. "
                    await self.game_change(username, game)
            else:
                # logger.info("No changes for " + username)
                # log_message += f"{username} no change. "
                continue
        if not log_message:
            logger.info(log_message)
