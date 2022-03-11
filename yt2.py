
import json
import aiohttp
import os
import datetime
import logging
import asyncio


logger = logging.getLogger('__main__.' + __name__)


class YouTubeAPI:
    """
    API wrapper to access YouTube API

    Attributes:
        id (str): ID for the YouTube channel to check for new videos on
        token (str): Access token for the YouTube API
        playlist_id (str): ID for the playlist to check for new videos
    """
    @classmethod
    async def create(cls, ID, token):
        """Function required to construct the class

        Because the playlist_id attribute requires an awaited function, we require calling
        this function to instatiate the class

        Args:
            ID (str): ID for the YouTube channel to check for new videos on
            token (str): Access token for the YouTube API

        Returns:
            class: An instance of the YouTubeAPI class
        """
        self = YouTubeAPI()
        self.id = ID
        self.token = token
        self.playlist_id = await self.recent_uploads()
        return self


    async def recent_uploads(self):
        """Fetch the recent uplaods playlist ID from the YouTube API using the id attribute

        Returns:
            str: ID for the recent uploads playlist
        """
        url = f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={self.id}&key={self.token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                c1 = await response.json()
                c = c1['items']
                playlist_id = c[0]['contentDetails']['relatedPlaylists']['uploads']
                await session.close()
        return playlist_id

    
    async def recent_playlist(self):
        """Fetch the recent playlist from the YouTube API

        Returns:
            list: List of dicts for each of the recent uploads
        """
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={self.playlist_id}&key={self.token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                response = await res.json()
                playlist = response['items']
                await session.close()
        return playlist


    async def latestvideo(self):
        """Determine the latest video on a channel and it's published time

        Returns:
            tuple: (ID string for latest video, string for time published)
        """
        playlist = await self.recent_playlist()
        latest = playlist[0]['contentDetails']['videoId']
        published_time = playlist[0]['contentDetails']['videoPublishedAt']
        return latest, published_time


class DiscordNotif:
    """
    Class running a loop to send a message in a channel on a new video upload

    Attributes:
        discord (class): Discord client object
        token (str): YouTube API access token
        ID (str): YouTube channel ID
        name (str): Name of the YouTube channel
        channel (str): Channel ID where message is sent
        message (str): Message to be sent when new video is uploaded
        cd (str): How often to check for a new video
        cd_post (str): Time to wait to check for a new video after an upload
        path (str): Path to a json where the past video IDs are stored
    """
    def __init__(self, discord, token, ID, name, channel, message, cd, cd_post, path):
        """Constructor for the DiscorNotif class

        Args:
            discord (class): Discord client object
            token (str): Youtube API access token
            ID (str): YouTube channel ID
            name (str): Name of the YouTube channel
            channel (str): Channel ID where the message is sent
            message (str): Message to be sent when new video is uploaded
            cd (str): How often to check for a new video
            cd_post (str): Time to wait to check for a new video after an upload
            path (str): Path to a json where the past video IDs are stored
        """
        self.discord = discord
        self.ID = ID
        self.token = token
        self.name = name #pretty sure I can take this out?
        self.channel = channel 
        self.message = message
        self.cd = cd
        self.cd_post = cd_post #cooldown after new video
        self.path = path #I can't have the past video list as self variable
    

    async def load_past_videos(self, path, client):
        """Load the list of past video IDs either from file or from the YouTube API

        Args:
            path (str): Path to json where the past video IDs are stored
            client (class): The YouTubeAPI class object

        Returns:
            list: List of past video IDs
        """
        if os.path.isfile(path):
            with open(path, 'r') as f:
                r = json.load(f)
                past_list = r['past_videos']
            return past_list
        else:
            recent_videos = await self.most_recent_videos(client)
            d = {"past_videos": recent_videos}
            with open(path, 'w') as f:
                f.write(json.dumps(d))
            return recent_videos
    

    def update_past_videos(self, path, videos):
        """Update the json when a new video is uploaded

        Args:
            path (str): Path to json where the past video IDs are stored
            videos (list): List of past video IDs
        """
        if os.path.isfile(path):
            d = {"past_videos": videos}
            with open(path, 'w') as f:
                f.write(json.dumps(d))
            

    async def most_recent_videos(self, client):
        """Fetch the most recent video IDs

        This is the function to be used when there is not a file containing
        the past video IDs.

        Args:
            client (class): YouTubeAPI class object

        Returns:
            list: List of past video IDs
        """
        recent_playlist = await client.recent_playlist()
        recent_videos = []
        for i in range(0,len(recent_playlist)):
            recent_videos.append(recent_playlist[i]['contentDetails']['videoId'])
        return recent_videos
    

    async def start_client(self):
        """Instantiate the YouTubeAPI class

        Returns:
            class: YouTube API class
        """
        client = await YouTubeAPI.create(self.ID, self.token)
        return client
    

    async def new_video_ping(self):
        """Function containing the loop to check for new IDs

        This function is to be added to the loop made when instantiating the 
        discord bot. 
        """
        client = await self.start_client()
        past_videos = await self.load_past_videos(self.path, client)
        latestvideo = await client.latestvideo()
        latest_id = latestvideo[0]
        if latest_id not in past_videos:
            past_videos.append(latest_id)
            self.update_past_videos(self.path, past_videos)
        logger.info("I AM STARTING THE WHILE LOOP")
        while True:
            currentDT = str(datetime.datetime.now())
            try:
                latestvideo = await client.latestvideo()
            except:
                continue
            check_id = latestvideo[0]
            if check_id in past_videos:
                logger.info(check_id + " most recent id checked at " + currentDT)
                await asyncio.sleep(self.cd)
            elif check_id != latest_id:
                channel = self.discord.get_channel(id=self.channel) #need this here because it has to exist after the bot starts
                youtube_l = "https://youtu.be/{}".format(check_id)
                logger.info("new video, posting notification")
                await channel.send(self.message.format(youtube_l))
                latest_id = check_id
                past_videos.append(check_id)
                self.update_past_videos(self.path, past_videos)
                await asyncio.sleep(self.cd)
            else:
                await asyncio.sleep(self.cd)