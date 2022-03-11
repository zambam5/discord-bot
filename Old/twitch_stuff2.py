import aiohttp, json
import cfg


class TwitchAPI:
    def __init__(self, ID, token):
        self.headers = {
                'Client-ID': ID,
                'Authorization': 'Bearer {}'.format(token)
            }


    async def get_game(self, gameid):
        '''twitch api reference:
        https://dev.twitch.tv/docs/api/reference#get-games
        '''
        url = f'https://api.twitch.tv/helix/games?id={gameid}'
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as res:
                response = await res.json()
                game = response['data'][0]['name']
                await session.close()
        return game
    

    async def get_status(self, username):
        '''twitch api reference
        https://dev.twitch.tv/docs/api/reference#get-streams
        '''
        url = f'https://api.twitch.tv/helix/streams?user_login={username}'
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as res:
                response = await res.json()
                print(response)
                try:
                    if response["status"] == 401:
                        status = ["expired"]
                        await session.close()
                except KeyError:
                    if response['data'] == []:
                        status = [False]
                        await session.close()
                    else:
                        gameid = response['data'][0]['game_id']
                        game = await self.get_game(gameid)
                        status = [True, game]
                        await session.close()
        return status
