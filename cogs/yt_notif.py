import json
import aiohttp
import os
import datetime
import logging
import asyncio
import random
import time
from cogs.APIs.youtube import YouTubeAPI
from discord.ext import tasks, commands
from setuptools import Command

logger = logging.getLogger("__main__." + __name__)


class YoutubeNotif(commands.Cog):
    """
    Class running a loop to send a message in a channel on a new video upload

    Attributes:
        bot (class): Discord client object
        token (str): YouTube API access token
    """

    def __init__(self, bot):

        self.bot = bot
        self.configpath = "config/yt-test.json"
        self.process_config(self.configpath)
        self.client = YouTubeAPI(self.TOKEN)
        self.past_videos = {}
        self.cds = {}
        self.mentions = {}
        self.discord = {}
        self.yt_loop.start()

    def process_config(self, configpath):
        if os.path.isfile(configpath):
            # check for existing config file
            with open(configpath, "r") as f:
                r = json.load(f)
            self.TOKEN = r["TOKEN"]
            self.TOKEN2 = r["TOKEN2"]
            self.notifications = r["NOTIFICATIONS"]
        # figure out what to do if no config file
        else:
            with open(configpath, "w"):
                f.write(json.dumps({}))

    async def most_recent_videos(self, channel):
        """Fetch the most recent video IDs

        This is the function to be used when there is not a file containing
        the past video IDs.

        Args:
            client (class): YouTubeAPI class object

        Returns:
            list: List of past video IDs
        """
        playlist_id = self.notifications[channel]["playlist_id"]
        recent_playlist = await self.client.recent_playlist(playlist_id)
        recent_videos = []
        for i in range(0, len(recent_playlist)):
            recent_videos.append(recent_playlist[i]["contentDetails"]["videoId"])
        return recent_videos[::-1]  # reverse the list so newest is last

    async def load_past_videos(self, path, channel):
        """Load the list of past video IDs either from file or from the YouTube API

        Args:
            path (str): Path to json where the past video IDs are stored

        Returns:
            list: List of past video IDs
        """
        if os.path.isfile(path):
            with open(path, "r") as f:
                r = json.load(f)
            if channel in r.keys():
                self.past_videos[channel] = r[channel]
                return
            else:
                recent_videos = await self.most_recent_videos(channel)
                r[channel] = recent_videos
                with open(path, "w") as f:
                    f.write(json.dumps(r))
                self.past_videos[channel] = r[channel]
        else:
            recent_videos = await self.most_recent_videos(channel)
            d = {channel: recent_videos}
            with open(path, "w") as f:
                f.write(json.dumps(d))
            self.past_videos = d

    def update_past_videos(self, path):
        """Update the json when a new video is uploaded

        Args:
            path (str): Path to json where the past video IDs are stored
            videos (list): List of past video IDs
        """
        if os.path.isfile(path):
            d = self.past_videos
            with open(path, "w") as f:
                f.write(json.dumps(d))

    async def latest_video_check(self, channel) -> list:
        """Take a YouTube channel and determine if the latest video is new

        Args:
            channel (str): Youtube channel name from config file
        """
        # last_video = self.past_videos[channel][-1]  # last item in list should be latest
        new_video = await self.client.latestvideo(
            self.notifications[channel]["playlist_id"]
        )
        if new_video[0] in self.past_videos[channel]:
            dt = str(datetime.datetime.now())
            print("%s no new video at %s" % (channel, dt))
            return [False]  # no new video, no extra info needed
        else:
            dt = str(datetime.datetime.now())
            logger.info("%s new video %s at %s", channel, new_video[0], dt)
            path = self.notifications[channel]["path"]
            self.past_videos[channel].append(new_video[0])
            self.update_past_videos(path)
            return [
                True,
                new_video[0],
                new_video[1],
            ]  # new video, ping will require the new id, new_video[1] determines if short

    async def new_video_ping(self, channel):
        results = await self.latest_video_check(channel)
        if results[0]:
            video = results[1]
            short = results[2]
            if short:
                message = random.choice(
                    self.notifications[channel]["messages"]["short"]
                )
                await self.discord[channel].send(message.format(video))
            else:
                role = self.mentions[channel]
                mention = role.mention
                message = random.choice(
                    self.notifications[channel]["messages"]["video"]
                )
                await self.discord[channel].send(message.format(mention, video))
            cd = self.notifications[channel]["cd_post_upload"]
            self.cds[channel] = time.time() + cd
        else:
            cd = self.notifications[channel]["cd"]
            self.cds[channel] = time.time() + cd

    async def initial_state(self):
        if self.past_videos == {}:
            logger.info("Getting initial state for Youtube extension")
            for channel in self.notifications.keys():
                path = self.notifications[channel]["path"]
                channel_id = self.notifications[channel]["ID"]
                playlist_id = await self.client.recent_uploads(channel_id)
                self.notifications[channel]["playlist_id"] = playlist_id
                await self.load_past_videos(path, channel)
                self.cds[channel] = time.time() + self.notifications[channel]["cd"]
                role = self.notifications[channel]["role"]
                guild = self.notifications[channel]["guild"]
                g = self.bot.get_guild(guild)
                self.mentions[channel] = g.get_role(role)
                c = self.notifications[channel]["channel"]
                self.discord[channel] = self.bot.get_channel(c)

    @tasks.loop(seconds=30)
    async def yt_loop(self):
        try:
            await self.initial_state()
            for channel in self.notifications.keys():
                if time.time() > self.cds[channel]:
                    await self.new_video_ping(channel)
                else:
                    continue
        except:
            logger.exception("Unhandled Exception: ")

    @yt_loop.before_loop
    async def before_yt_loop(self):
        logger.info("youtube notifs waiting for bot")
        await self.bot.wait_until_ready()


async def setup(bot):
    logger.info("Youtube notifs loaded")
    await bot.add_cog(YoutubeNotif(bot))
