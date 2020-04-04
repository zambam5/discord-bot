
import cfg, json, aiohttp

async def latestvideo():
    url = f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={cfg.YT_ID}&key={cfg.YT_TOKEN}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            c1 = await response.json()
            c = c1['items']
            v_id = c[0]['contentDetails']['relatedPlaylists']['uploads']
    url2 = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={v_id}&key={cfg.YT_TOKEN}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url2) as response:
            playlist1 = await response.json()
            playlist = playlist1['items'][0]
            latest = playlist['contentDetails']['videoId']
            published_time = playlist['contentDetails']['videoPublishedAt']
    return latest, published_time
