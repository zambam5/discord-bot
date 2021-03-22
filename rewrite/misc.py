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

class Misc(commands.Cog):
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        if ctx.message.channel.id == self.channel:
            logger.info('ping received')
            channel = ctx.message.channel
            try:
                taskset = asyncio.Task.all_tasks(self.bot.loop)
                tasklist = []
                print(tasklist)
                await channel.send('beep boop')
                await channel.send('I am running ' + str(len(taskset)) + ' tasks')
            except:
                await channel.send('failure :(')
                logger.exception("message: ")


if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)

r_config = config['MISC']['PING']

def setup(bot):
    bot.add_cog(Misc(bot, r_config['channel']))