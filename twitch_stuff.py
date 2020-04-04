import aiohttp, json
import cfg

token = cfg.TTV_TOKEN
ID = cfg.TTV_ID

async def get_user_id(username):
    headers = {
            'Client-ID': ID,
            'Authorization': 'Bearer {}'.format(token)
        }
    url = "https://api.twitch.tv/helix/users?login={}".format(username)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            try:
                userid1 = await response.json()
                userid = userid1['users'][0]['id']
                return userid
            except:
                print(response)
                return False


async def get_status(userid):
    headers = {
            'Client-ID': ID,
            'Authorization': 'Bearer {}'.format(token)
        }
    url = 'https://api.twitch.tv/helix/streams?user_login={}'.format(userid)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as res:
            response = await res.json()
            print(userid, response['data'])
            if response['data'] == []:
                print('not live')
                return False
            else:
                print('live')
                return True
