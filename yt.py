
import cfg, json, requests

def latestvideo():
    url = f'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={cfg.YT_ID}&key={cfg.YT_TOKEN}'
    response = requests.get(url)
    c = response.json()['items']
    v_id = c[0]['contentDetails']['relatedPlaylists']['uploads']
    url2 = f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={v_id}&key={cfg.YT_TOKEN}'
    response = requests.get(url2)
    playlist= response.json()['items'][0]
    latest = playlist['contentDetails']['videoId']
    published_time = playlist['contentDetails']['videoPublishedAt']
    return latest,published_time
