import setuptools
import json
import aiohttp
import os
import datetime
import logging
import asyncio
import time

from discord.ext import tasks, commands
from setuptools import Command

logger = logging.getLogger('__main__.' + __name__)

class Reminders(commands.Cog):
    """This is a class for a reminder command in a discord bot

    Attributes:
        bot (class): The discord.py bot object
        path (str): The file path to a json where the reminders are stored
        reminder_list (list): List of reminders, each formatted as a dict
        channels (list): List of IDs (ints) for channels where the remindme command can be used
        units (dict): [time unit]: [int of time unit in seconds]
        limit (int): How far in advance a user is allowed to set reminders
    """
    def __init__(self, bot, path, channels, units, limit):
        """The constructor for the Reminders class

        Args:
            bot (class): The discord.py bot object
            path (str): The file path to a json where the reminders are stored
            channels (list): List of IDs (ints) for channels where the remindme command can be used
            units (dict): Dictionary containing conversion from time unit symbol to time in seconds
            limit (int): How far in advance a user is allowed to set reminders
        """
        self.bot = bot
        self.reminder_list = self.load_reminder_list(path)
        self.path = path
        self.channels = channels
        self.time_units = units
        self.limit = limit
        #what else do I need?
        self.check_reminders.start()

    def load_reminder_list(self, path):
        """Function to load list of existing reminders from the path attribute

        Args:
            path (str): Path containing the json of saved reminders

        Returns:
            list: List of reminders, each of which is a dict
        """
        if os.path.isfile(path):
            with open(path, 'r') as f:
                reminder_list = json.load(f)
        else:
            reminder_list = []
        return reminder_list
    
    @commands.command()
    async def remindme(self, ctx):
        """
        Reminder command
        ~!remindme [time length] [time unit (d, h, m, s)] [reminder message]
        Example:
        ~!remindme 1 m Reminder in 1 minute
        will remind you with the message
        "@you here is your reminder for Reminder in 1 minute
        """
        message = ctx.message
        channel = message.channel
        if channel.id in self.channels:
            #do stuff
            m = message.content[9:].split(' ')
            if len(m) < 4:
                await channel.send('Be sure you are formatting the command correctly')
            quantity = int(m[1])
            if quantity < 1:
                await channel.send('Quantity must not be 0 or negative')
                return
            unit = m[2]
            if unit not in self.time_units.keys():
                await channel.send('Unit must be one of days(d), hours(h), minutes(m), or seconds(s); and not a mix of the four')
                return
            reminder = ''.join(word+" " for word in m[3:])
            name = message.author.mention
            seconds = quantity*self.time_units[unit]
            if seconds >= self.limit:
                await channel.send('That is too far in the future I may be dead <:FeelsStrongMan:795264167107100692>')
                return
            else:
                remindtime = time.time() + seconds
                self.reminder_list.append(
                    {
                        'future': remindtime,
                        'author': name,
                        'reminder': reminder,
                        'channel': channel.id
                    }
                )
                await channel.send(name + " I will remind you in {} seconds".format(seconds))
                with open(self.path, 'w') as f:
                    f.write(json.dumps(self.reminder_list))
                return
    
    @tasks.loop(seconds=5.0)
    async def check_reminders(self):
        """The loop to check for reminders.

        This function checks every 5 seconds if it needs to remind someone, then if a reminder
        is more than one minute in the past removes it from the reminder_list.
        """
        to_remove = [] #the list of reminders that have passed
        for reminder in self.reminder_list:
            if time.time() - reminder['future'] > 60:
                to_remove.append(reminder)
            elif reminder['future'] <= time.time():
                channel = self.bot.get_channel(reminder['channel'])
                await channel.send(reminder['author'] + " here is your reminder for " + reminder['reminder'])
                to_remove.append(reminder)
        if to_remove:
            leftovers = [x for x in self.reminder_list if x not in to_remove]
            self.reminder_list = leftovers
            with open(self.path, 'w') as f:
                f.write(json.dumps(self.reminder_list))
    
    @check_reminders.before_loop
    async def before_check_reminders(self):
        """Delay start of the loop until the bot object gives the ready event
        """
        await self.bot.wait_until_ready()

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)

r_config = config['REMINDERS']

def setup(bot):
    logger.info('Reminders loaded')
    bot.add_cog(Reminders(bot, r_config['path'], r_config['channels'], r_config['time_units'], r_config['limit']))
