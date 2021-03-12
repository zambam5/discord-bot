import discord
from discord.ext.commands import Bot
from discord.ext import tasks
from discord import Intents
import asyncio
import logging
import datetime
import re
import time
import gc
import json
import configparser
import os.path
#local modules:
import twitch_stuff2, yt2
#from reminders import Reminders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
#logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

'''config = configparser.ConfigParser()
config.read('cfg.ini')
print(config['YOUTUBE']['TOKEN'])



yt_token = str(config['YOUTUBE']['TOKEN'])
yt_id = str(config['YOUTUBE']['ID'])'''

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)


twitch = dict()
youtube = dict()

intents = Intents()
intents.guilds = True
intents.members = True
intents.presences = True
intents.messages = True
intents.reactions = False #THIS IS SUBJECT TO CHANGE
bot = Bot(intents=intents, command_prefix='~!')

'''@bot.event
async def on_message(message):
    print('message received')'''


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you struggle"))
    logger.info("Logged in as " + bot.user.name)


bot.load_extension("reminders")
#instantiate the youtube objects
#begin the background tasks
for chan in config['YOUTUBE']['NOTIFICATIONS']:
    c = config['YOUTUBE']
    TOKEN = c['TOKEN']
    ID = c['NOTIFICATIONS'][chan]['ID']
    channel = c['NOTIFICATIONS'][chan]['channel']
    message = c['NOTIFICATIONS'][chan]['message']
    cd = c['NOTIFICATIONS'][chan]['cd']
    cd_post = c['NOTIFICATIONS'][chan]['cd_post_upload']
    path = c['NOTIFICATIONS'][chan]['path']
    currentDT = str(datetime.datetime.now())
    youtube[chan] = yt2.DiscordNotif(bot, TOKEN, ID, chan, channel, message, cd, cd_post, path)
    try:
        logger.info('creating youtube loop for ' + chan + ' at ' + currentDT)
        bot.loop.create_task(youtube[chan].new_video_ping())
    except:
        logger.exception('message :')

#instantiate the twitch objects
#begin the background tasks
for stream in config['TWITCH']['NOTIFICATIONS'].keys():
    ID = config['TWITCH']['ID']
    TOKEN = config['TWITCH']['TOKEN']
    channels = config['TWITCH']['NOTIFICATIONS'][stream]['channels']
    messages = config['TWITCH']['NOTIFICATIONS'][stream]['messages']
    cd = config['TWITCH']['NOTIFICATIONS'][stream]['cd']
    twitch[stream] = twitch_stuff2.DiscordNotif(bot, ID, TOKEN, stream, channels, messages, cd)
    try:
        logger.info('creating loop for ' + stream)
        bot.loop.create_task(twitch[stream].live_ping())
    except:
        logger.exception('message: ')


TOKEN = str(config['DISCORD']['TOKEN'])
logger.info(TOKEN)
try:
    print("starting bot")
    bot.run(TOKEN)
except:
    logger.exception('message: ')

