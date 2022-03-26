import aiohttp, json, datetime, logging, time, os


logger = logging.getLogger("__main__." + __name__)


class TwitchAPI:
    @classmethod
    async def create(cls, ID: str, secret: str, path: str):
        """Create an instance of the Twitch API client

        Args:
            ID (str): ID for accessing the API
            secret (str): client secret
            path (str): path to store credentials

        Returns:
            _type_: an instance of Twitch API
        """
        self = TwitchAPI()
        self.ID = ID
        self.secret = secret
        self.path = path
        await self.get_auth(ID, secret)
        return self

    def set_headers(self, ID: str, access_token: str):
        """Sets the self attribute for the request header

        Args:
            ID (str): ID to access Twitch API
            access_token (str): Access token to access Twitch API
        """
        self.headers = {"Client-ID": ID, "Authorization": "Bearer " + access_token}

    async def get_auth(self, ID: str, secret: str, refresh=False):
        """Creates a class attribute for the twith authorization

        Args:
            ID (str): ID to access Twitch API
            secret (str): client secret
            refresh (bool, optional): Set to True if a request failed requiring new auth. Defaults to False.

        Returns:
            None: no actual return, return only used to end function early
        """
        # start by checking if there's an existing file
        if os.path.isfile(self.path) and not refresh:
            with open(self.path, "r") as f:
                r = json.load(f)
            # check if existing token has expired
            if time.time() - r["time_created"] > r["expires_in"]:
                # token expired
                pass  # let the rest of the function run to get new token
            else:
                # token is still good
                access_token = r["access_token"]
                currentDT = str(datetime.datetime.now())
                logger.info("Access token retrieved from file at " + currentDT)
                self.set_headers(ID, access_token)
                self.access_token = access_token
                return  # need to stop the function here
        # either no existing token or token requires refresh
        body = {
            "client_id": ID,
            "client_secret": secret,
            "grant_type": "client_credentials",
        }
        url = "https://id.twitch.tv/oauth2/token"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=body) as res:
                response = await res.json()
                response["time_created"] = time.time()
                access_token = response["access_token"]
                await session.close()
        with open(self.path, "w") as f:
            f.write(json.dumps(response))
        currentDT = str(datetime.datetime.now())
        logger.info("Access Token refreshed " + currentDT)
        self.set_headers(ID, access_token)
        self.access_token = access_token

    async def get_game(self, gameid):
        """twitch api reference:
        https://dev.twitch.tv/docs/api/reference#get-games
        this is no longer needed but I'm leaving it
        """
        url = f"https://api.twitch.tv/helix/games?id={gameid}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as res:
                response = await res.json()
                game = response["data"][0]["name"]
                await session.close()
        return game

    async def get_status(self, usernames: list):
        """Fetch the current status of a stream from the Twitch API

        Reference for the Twitch API https://dev.twitch.tv/docs/api/reference#get-streams

        Args:
            usernames (list): List of usernames of the streamers whose status are being checked

        Returns:
            response (list): full list from "data" in the response
                special cases:
                    []: all checked streams are not live
                    ["expired"]: the auth token is expired
        """
        login_params = "user_login=" + "&user_login=".join(usernames)
        # should look like user_login=[0]&user_login=[1]&user_login=[2]...
        url = f"https://api.twitch.tv/helix/streams?{login_params}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as res:
                response = await res.json()
                if "status" in response.keys():
                    if response["status"] == 401:
                        await self.get_auth(self.ID, self.secret, refresh=True)
                        status = ["expired"]
                        await session.close()
                else:
                    status = response["data"]
                    await session.close()
        return status
