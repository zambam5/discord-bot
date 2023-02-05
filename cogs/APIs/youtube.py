import json
import aiohttp
import os
import datetime
import logging
import asyncio

logger = logging.getLogger("__main__." + __name__)


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
        """Fetch the recent uploads playlist ID from the YouTube API using the id attribute

        Args:
            ID (str): ID of a youtube channel

        Returns:
            str: ID for the recent uploads playlist
        """
        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={ID}&key={self.token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                c1 = await response.json()
                c = c1["items"]
                playlist_id = c[0]["contentDetails"]["relatedPlaylists"]["uploads"]
                await session.close()
        return playlist_id

    async def recent_playlist(self, playlist_id):
        """Fetch the recent playlist from the YouTube API

        Returns:
            list: List of dicts for each of the recent uploads
        """
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&part=snippet&playlistId={playlist_id}&key={self.token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                response = await res.json()
                playlist = response["items"]
                await session.close()
        return playlist

    async def video(self, video_id):
        # no current functionality
        # could be useful to access information on if a video is a live broadcast
        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=liveStreamingDetails&id={video_id}&key={self.token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                response = await res.json()

    async def latestvideo(self, playlist_id):
        """Determine the latest video on a channel and it's published time

        Returns:
            tuple: (ID string for latest video, string for time published)
        """
        playlist = await self.recent_playlist(playlist_id)
        latest = playlist[0]["contentDetails"]["videoId"]
        # published_time = playlist[0]["contentDetails"]["videoPublishedAt"]
        description = playlist[0]["snippet"]["description"]
        if "#shorts" in description:
            short = True
        else:
            short = False
        return latest, short

    async def check_for_short(self, video_id):
        # Youtube will return a redirect 303 code for a non-short video
        # Sadly does not work on my Digital Ocean server cause DO is blacklisted by Google
        url = f"https://www.youtube.com/shorts/{video_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=False) as res:
                logger.info("Response code for %s: %s", video_id, res.status)
                print(res.headers)
                if res.status == 303 or res.status == 302:
                    return False
                else:
                    return True


async def test():
    path = "config/yt-test.json"
    if os.path.isfile(path):
        # check for existing config file
        with open(path, "r") as f:
            r = json.load(f)
        TOKEN = r["TOKEN"]
    yt = YouTubeAPI(TOKEN)
    playlist = await yt.recent_uploads("UCN90AEOAJES1y2cYn0SsR5A")
    x = await yt.latestvideo(playlist)
    print(x)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test())
