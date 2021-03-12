import json
import aiohttp
import os
import datetime
import logging
import asyncio
import time

from discord.ext import tasks, commands

logger = logging.getLogger(__name__)

class Reminders(commands.Cog):
    def __init__(self, bot, path, channels, units, limit):
        print("starting reminders class")
        self.bot = bot
        self.reminder_list = self.load_reminder_list(path)
        self.path = path
        self.channels = channels
        self.time_units = units
        self.limit = limit
        #what else do I need?
        self.check_reminders.start()

    def load_reminder_list(self, path):
        if os.path.isfile(path):
            with open(path, 'r') as f:
                reminder_list = json.load(f)
        else:
            reminder_list = []
        return reminder_list
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('We ready')
    
    @commands.command(name='remindme')
    async def remindme(self, ctx):
        '''
        Reminder command
        ~!remindme [time length] [time unit (d, h, m, s)] [reminder message]
        Example:
        ~!remindme 1 m Reminder in 1 minute
        will remind you with the message
        "@you here is your reminder for Reminder in 1 minute
        This command is only available in 2 channels
        '''
        print("we got here")
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
        print("checking reminders")
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
        print('waiting...')
        await self.bot.wait_until_ready()

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)

r_config = config['REMINDERS']

def setup(bot):
    bot.add_cog(Reminders(bot, r_config['path'], r_config['channels'], r_config['time_units'], r_config['limit']))
'''
async def remind_me(message, reminders):
    if message.guild.id != 504675193751601152:
        return reminders
    elif message.content.startswith('!remindme'):
        channel = message.channel
        m = message.content.split(' ')
        quantity = int(m[1])
        if quantity < 1:
            await channel.send('Quantity must not be 0 or negative')
            return reminders
        unit = m[2]
        if unit not in time_units.keys():
            await channel.send('Unit must be hours(h), minutes(m), or seconds(s) and also not a mix of the three')
            return reminders
        reminder = ''.join(word +" " for word in m[3:])
        name = message.author.mention
        seconds = quantity*time_units[unit]
        if seconds >= 1209600:
            await channel.send('That is too far in the future I may be dead <:FeelsStrongMan:795264167107100692>')
            return reminders
        else:
            remindtime = time.time()+seconds
            reminders.append(
                {
                'future': remindtime,
                'author': name,
                'reminder': reminder,
                'channel': channel.id
                }
            )
            logger.info('reminder added for ' + str(message.author))
            await channel.send(name + " I will remind you in {} seconds".format(seconds))
            with open('reminders.json', 'w') as f:
                f.write(json.dumps(reminders))
            return reminders
    else:
        return reminders


async def check_reminders():
    global reminder_list
    while True:
        to_remove = []
        for reminder in reminder_list:
            if time.time() - reminder['future'] > 60:
                to_remove.append(reminder)
            elif reminder['future'] <= time.time():
                channel = client.get_channel(reminder['channel'])
                await channel.send(reminder['author'] + " here is your reminder for " + reminder['reminder'])
                to_remove.append(reminder)
                logger.info('reminder removed')
        if to_remove:
            leftovers = [x for x in reminder_list if x not in to_remove]
            reminder_list = leftovers
            with open('reminders.json', 'w') as f:
                f.write(json.dumps(reminder_list))
        await asyncio.sleep(5)
'''