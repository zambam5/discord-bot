from twitch import TwitchClient
import requests, json
import cfg

token = cfg.TTV_TOKEN
ID = cfg.TTV_ID

def get_user_id(username):
    headers = {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': ID,
            'Authorization': 'OAuth {}'.format(token)
        }
    url = "https://api.twitch.tv/kraken/users?login={}".format(username)
    response = requests.get(url, params=None, headers=headers).json()
    try:
        userid = response['users'][0]['_id']
        return userid
    except:
        print(response)
        return False


def get_status(userid):
    headers = {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': ID,
        }
    url = 'https://api.twitch.tv/kraken/streams/{}'.format(userid)
    response = requests.get(url, params=None, headers=headers).json()
    print(response)
    try:
        if response['stream']==None:
            return False
        else:
            return True
    except:
        print('we have a problem here')
        return
