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
    
    def __init__(self, token):
        """constructor class for YoutubeAPI

        Args:
            token (str): Access token for the YouTube API
        """
        self.token = token


    async def recent_uploads(self, ID):
        """Fetch the recent uplaods playlist ID from the YouTube API using the id attribute
        
        Args:
            ID (str): ID of a youtube channel

        Returns:
            str: ID for the recent uploads playlist
        """
        url = f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={ID}&key={self.token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                c1 = await response.json()
                c = c1['items']
                playlist_id = c[0]['contentDetails']['relatedPlaylists']['uploads']
                await session.close()
        return playlist_id

    
    async def recent_playlist(self, playlist_id):
        """Fetch the recent playlist from the YouTube API

        Returns:
            list: List of dicts for each of the recent uploads
        """
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&key={self.token}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                response = await res.json()
                playlist = response['items']
                await session.close()
        return playlist


    async def latestvideo(self, playlist_id):
        """Determine the latest video on a channel and it's published time

        Returns:
            tuple: (ID string for latest video, string for time published)
        """
        playlist = await self.recent_playlist(playlist_id)
        latest = playlist[0]['contentDetails']['videoId']
        published_time = playlist[0]['contentDetails']['videoPublishedAt']
        return latest, published_time