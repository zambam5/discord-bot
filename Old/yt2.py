
import json
import aiohttp

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
                print(c1)
                c = c1['items']
                playlist_id = c[0]['contentDetails']['relatedPlaylists']['uploads']
                await session.close()
        return playlist_id


    async def latestvideo(self):
        
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={self.playlist_id}&key={self.token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                response = await res.json()
                playlist = response['items'][0]
                latest = playlist['contentDetails']['videoId']
                published_time = playlist['contentDetails']['videoPublishedAt']
                await session.close()
        return latest, published_time
