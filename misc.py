import setuptools
import json
import os
import logging
import asyncio
from discord import utils
from discord import ActivityType

from discord.ext import tasks, commands
from setuptools import Command

logger = logging.getLogger('__main__.' + __name__)

def check_if_it_is_me(ctx):
    return ctx.message.author.id == 297516831227510786

class Misc(commands.Cog):
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        
    
    @commands.command(name='ping')
    #@commands.check(check_if_it_is_me)
    async def _ping(self, ctx):
        logger.info('we got here')
        if ctx.message.channel.id == self.channel:
            logger.info('ping received')
            #channel = ctx.message.channel
            try:
                taskset = asyncio.all_tasks(self.bot.loop)
                tasklist = []
                print(tasklist)
                await ctx.send('beep boop')
                await ctx.send('I am running ' + str(len(taskset)) + ' tasks')
            except:
                await ctx.send('failure :(')
                logger.exception("message: ")

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)

r_config = config['MISC']['PING']

def setup(bot):
    bot.add_cog(Misc(bot, r_config['channel']))