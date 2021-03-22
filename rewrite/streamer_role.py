import json
import aiohttp
import os
import datetime
import logging
import asyncio
import time
from discord import utils
from discord import ActivityType

from discord.ext import tasks, commands

logger = logging.getLogger('__main__.' + __name__)

class StreamerRole(commands.Cog):
    """The goal of this class is to give people whose discord activity shows streaming, and give them the Live role

    Attributes:
        bot (class): The discord.py bot object
        guild (int): The ID for the guild where the streamer role is to be managed
        streamer_role (str): The name of the role with all the people to be checked if streaming
        live_role (str): The name of the role to be given to those that are streaming
    """
    def __init__(self, bot, guild, streamer, live):
        """Constructor for the StreamerRole class

        Args:
            bot (class): The discord.py bot object
            guild (int): The ID for the guild where the streamer role is to be managed
            streamer (str): The name of the role with the people who can be given the live role
            live (str): The name of the role given when someone in the streamer role is streaming
        """
        self.bot = bot
        self.guild = guild #this needs to be converted to a guild object
        self.streamer_role = streamer
        self.live_role = live
        self.streamer_mode.start()

    @tasks.loop(seconds=300)
    async def streamer_mode(self):
        """The function to check who needs to be given the live role, and who needs it removed
        """
        guild = self.bot.get_guild(self.guild)
        role = utils.get(guild.roles, name=self.streamer_role)
        liverole = utils.get(guild.roles, name=self.live_role)
        streamers = role.members
        logger.info("Running the live role check")
        for streamer in streamers:
            if liverole in streamer.roles:
                if streamer.activity == None:
                    await streamer.remove_roles(liverole)
                    continue
                for a in streamer.activities:
                    if a.type == ActivityType.streaming:
                        live = True
                        break
                    else:
                        live = False
                if not live:
                    await streamer.remove_roles(liverole)
            else:
                if streamer.activity == None:
                    continue
                for a in streamer.activities:
                    if a.type == ActivityType.streaming:
                        await streamer.add_roles(liverole)
                        break
                    else:
                        continue
    
    @streamer_mode.before_loop
    async def before_streamer_mode(self):
        """Delay start of the loop until the bot object gives the ready event
        """
        await self.bot.wait_until_ready()


if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)

r_config = config['STREAMER_ROLE']

def setup(bot):
    bot.add_cog(StreamerRole(bot, r_config['guild'], r_config['streamer_role'], r_config['live_role']))