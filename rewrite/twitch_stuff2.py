import aiohttp, json, datetime, logging, asyncio


logger = logging.getLogger(__name__)

class TwitchAPI:
    #need to add something for refreshing the token
    def __init__(self, ID, token):
        self.headers = {
                'Client-ID': ID,
                'Authorization': 'Bearer {}'.format(token)
            }


    async def get_game(self, gameid):
        '''twitch api reference:
        https://dev.twitch.tv/docs/api/reference#get-games
        this is no longer needed but I'm leaving it
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
                if "status" in response.keys():
                    if response['status'] == 401:
                        status = ["expired"]
                        await session.close()
                else:
                    if response['data'] == []:
                        status = [False]
                        await session.close()
                    else:
                        gameid = response['data'][0]['game_id']
                        if gameid == '':
                            game = 'Unlisted'
                        else:
                            game = response['data'][0]['game_name']
                        status = [True, game]
                        await session.close()
        return status


class DiscordNotif:
    def __init__(self, discord, ID, token, stream, channels, messages, cd):
        '''
        discord - type: class? - the discord client from bot2.py
        ID - type: str - twitch ID for above class
        token - type: str - twitch token for above class
        stream - type: str - the stream to check for live
        channels - type: dict - channel ids for error messages or pings
        messages - type: dict - contains the various types of messages to send
        cd - type: dict - {'online': type: int - length between calls while online
                            'offline': type: int - length between calls while offline}
        '''
        self.discord = discord
        self.client = TwitchAPI(ID, token)
        self.stream = stream
        self.channels = channels
        self.messages = messages
        self.cd = cd
    

    def is_me(self, m):
        return m.author == client.user
    

    async def check_live(self, streamid, live_check):
        currentDT = str(datetime.datetime.now())
        try:
            new_check = await self.client.get_status(streamid)
        except:
            logger.exception('message: ')
            return live_check, "error"
        if "expired" in new_check:
            return "expired"
        elif new_check == live_check:
            logger.info(streamid + ' no status change as of ' + currentDT)
            return new_check, False
        else:
            if not live_check[0]:
                logger.info(streamid + ' live at ' + currentDT)
                return new_check, 'live' #purge and post message
            elif not new_check[0]:
                logger.info(streamid + ' offline at ' + currentDT)
                return new_check, 'offline' #purge and post message
            else:
                logger.info(streamid + ' game change at ' + currentDT)
                return new_check, 'game'
    

    async def live_ping(self):
        live_check = await self.client.get_status(self.stream)
        while True:
            check = await self.check_live(self.stream, live_check)
            if check == "expired":
                channel = self.discord.get_channel(id=self.channels['error'])
                channel.send('token expired, pls fix')
                await asyncio.sleep(self.cd['expired'])
            elif check[1] == "error":
                channel = self.discord.get_channel(id=self.channels['error'])
                channel.send('something broke, pls fix')
                await asyncio.sleep(self.cd['error'])
            else:
                live_check1 = check[0]
                job = check[1]
                if not job:
                    live_check = live_check1
                elif job == 'live':
                    game = live_check1[1]
                    message = self.messages['ping'].format(game)
                    channel = self.discord.get_channel(id=self.channels['ping'])
                    await channel.send(message)
                    live_check = live_check1
                elif job == 'offline':
                    currentDT = str(datetime.datetime.now())
                    logger.info('purging messages at ' + currentDT)
                    channel = self.discord.get_channel(id=self.channels['ping'])
                    await channel.purge(limit=100, check=self.is_me)
                    if self.messages['offline'] != False:
                        message = self.messages['offline']
                        await channel.send(message)
                    live_check = live_check1
                elif job == 'game':
                    game = live_check1[1]
                    message = self.messages['game'].format(game)
                    channel = self.discord.get_channel(id=self.channels['ping'])
                    await channel.send(message)
                    live_check = live_check1
                if live_check[0]:
                    await asyncio.sleep(self.cd['online'])
                else:
                    await asyncio.sleep(self.cd['offline'])

