import aiohttp, json, datetime, logging, asyncio, time, os


logger = logging.getLogger('__main__.' + __name__)

class TwitchAPI:
    """API wrapper for the Twitch API

    Attributes:
        header (dict): The header used when making a request to the Twitch API
    """    
    @classmethod
    async def create(cls, ID, secret, path):
        self = TwitchAPI()
        self.ID = ID
        self.secret = secret
        self.path = path
        await self.get_auth(ID, secret)
        return self


    def set_headers(self, ID, access_token):
        self.headers = {
            'Client-ID': ID,
            'Authorization': 'Bearer ' + access_token
            }

    async def get_auth(self, ID, secret, refresh = False):
        if os.path.isfile(self.path) and not refresh:
            with open(self.path, 'r') as f:
                r = json.load(f)
            if time.time() - r["time_created"] > r["expires_in"]:
                pass #let the rest of the function run
            else:
                access_token = r['access_token']
                currentDT = str(datetime.datetime.now())
                logger.info('Access token retrieved from file at ' + currentDT)
                self.set_headers(ID, access_token)
                self.access_token = access_token
                return #need to stop the function here
        body = {
            'client_id': ID,
            'client_secret': secret,
            'grant_type': 'client_credentials'
        }
        url = 'https://id.twitch.tv/oauth2/token'
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url,params=body) as res:
                response = await res.json()
                #print(response)
                response['time_created'] = time.time()
                access_token = response['access_token']
                await session.close()
        with open(self.path, 'w') as f:
            f.write(json.dumps(response))
        currentDT = str(datetime.datetime.now())
        logger.info('Access Token refreshed' + currentDT)
        self.set_headers(ID, access_token)
        self.access_token = access_token
                

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
        """Fetch the current status of a stream from the Twitch API

        Reference for the Twitch API https://dev.twitch.tv/docs/api/reference#get-streams

        Args:
            username (str): Username of the streamer whose status is being check

        Returns:
            list: A list corresponding to various responses from the request
        """
        url = f'https://api.twitch.tv/helix/streams?user_login={username}'
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as res:
                response = await res.json()
                if "status" in response.keys():
                    if response['status'] == 401:
                        await self.get_auth(self.ID, self.secret, refresh=True)
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
    """Class to setup discord notification when a stream goes live
    """
    def __init__(self, discord, ID, secret, stream, channels, messages, cd, path):
        """Constructor for the DiscordNotif class

        Args:
            discord (class): Discord client object
            ID (str): Twitch API ID
            token (str): OAuth token corresponding to the ID for the Twitch API
            stream (str): Name of the stream
            channels (list): List of various channels to send messages, depending on type
            messages (list): List of messages to send, depending on type
            cd (dict): Different cooldowns before checking the stream status, depending on most recent status
        """
        self.discord = discord
        self.stream = stream
        self.channels = channels
        self.messages = messages
        self.ID = ID
        self.secret = secret
        self.cd = cd
        self.path = path
    

    def is_me(self, m):
        """Function to check if the user is the bot

        Args:
            m (class): Message object from the Discord module

        Returns:
            bool: True or False depending on if the user is the bot
        """
        return m.author == self.discord.user
    
    
    async def start_client(self):
        """Instantiate the TwitchAPI class

        Returns:
            class: Twitch API class
        """
        self.client = await TwitchAPI.create(self.ID, self.secret, self.path)
    

    async def check_live(self, streamid, live_check):
        """Check the stream status

        Args:
            streamid (str): Name of the stream
            live_check (list): Most recent status of the stream

        Returns:
            list: Current status of the stream
        """
        currentDT = str(datetime.datetime.now())
        try:
            new_check = await self.client.get_status(streamid)
        except:
            logger.exception('message: ')
            return live_check, "error"
        if "expired" in new_check:
            new_check = await self.client.get_status(streamid)
            if new_check == live_check:
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
        """Setup a loop to check the status of a stream

        This function is to be added to the loop made when instantiating the 
        discord bot. 
        """
        await self.start_client()
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

