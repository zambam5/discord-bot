
import json
import aiohttp
import os
import datetime
import logging
import asyncio


logger = logging.getLogger(__name__)


class YouTubeAPI:
    @classmethod
    async def create(cls, ID, token):
        self = YouTubeAPI()
        self.id = ID
        self.token = token
        self.playlist_id = await self.recent_uploads()
        return self


    async def recent_uploads(self):
        url = f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={self.id}&key={self.token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                c1 = await response.json()
                c = c1['items']
                playlist_id = c[0]['contentDetails']['relatedPlaylists']['uploads']
                await session.close()
        return playlist_id

    
    async def recent_playlist(self):
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={self.playlist_id}&key={self.token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                response = await res.json()
                playlist = response['items']
                await session.close()
        return playlist


    async def latestvideo(self):
        playlist = await self.recent_playlist()
        latest = playlist[0]['contentDetails']['videoId']
        published_time = playlist[0]['contentDetails']['videoPublishedAt']
        return latest, published_time


class DiscordNotif:
    def __init__(self, discord, token, ID, name, channel, message, cd, cd_post, path):
        self.discord = discord
        self.ID = ID
        self.token = token
        self.name = name
        self.channel = channel 
        self.message = message
        self.cd = cd
        self.cd_post = cd_post #cooldown after new video
        self.path = path #I can't have the past video list as self variable
    

    async def load_past_videos(self, path, client):
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
        if os.path.isfile(path):
            d = {"past_videos": videos}
            with open(path, 'w') as f:
                f.write(json.dumps(d))
            

    async def most_recent_videos(self, client):
        recent_playlist = await client.recent_playlist()
        recent_videos = []
        for i in range(0,len(recent_playlist)):
            recent_videos.append(recent_playlist[i]['contentDetails']['videoId'])
        return recent_videos
    

    async def start_client(self):
        client = await YouTubeAPI.create(self.ID, self.token)
        return client
    

    async def new_video_ping(self):
        client = await self.start_client()
        channel = self.discord.get_channel(id=self.channel)
        past_videos = await self.load_past_videos(self.path, client)
        latestvideo = await client.latestvideo()
        latest_id = latestvideo[0]
        if latest_id not in past_videos:
            past_videos.append(latest_id)
            self.update_past_videos(self.path, past_videos)
        print("I AM STARTING THE WHILE LOOP")
        while True:
            currentDT = str(datetime.datetime.now())
            try:
                latestvideo = await client.latestvideo()
            except:
                print("ERROR")
                continue
            check_id = latestvideo[0]
            print(check_id)
            if check_id in past_videos:
                print("RECENT VIDEO KNOWN")
                logger.info(check_id + " most recent id checked at " + currentDT)
                await asyncio.sleep(self.cd)
            elif check_id != latest_id:
                youtube_l = "https://youtu.be/{}".format(check_id)
                await channel.send(self.message.format(youtube_l))
                latest_id = check_id
                past_videos.append(check_id)
                self.update_past_videos(self.path, past_videos)
                await asyncio.sleep(self.cd_post)
            else:
                await asyncio.sleep(self.cd)