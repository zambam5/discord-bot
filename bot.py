#
import discord
import random, cfg, yt, twitch_stuff
import asyncio, logging, datetime
import re
import regexgen
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('discordbot.log', mode='w')
formatter = logging.Formatter('''%(asctime)s -
                              %(name)s - %(levelname)s - %(message)s''')
handler.setFormatter(formatter)
logger.addHandler(handler)


TOKEN = cfg.D_TOKEN

#Setup for background tasks
checkedids = ["7NzVI2qCKh8", "4hcVIm0IiP4"]
latest_id = yt.latestvideo()[0]
checkedids.append(latest_id)

me_id = twitch_stuff.get_user_id('zambam5')
emongg_id = twitch_stuff.get_user_id('emongg')
if not emongg_id:
    print('no id for emongg monkaS')
    have_emongg = False
else:
    have_emongg = True

if not me_id:
    print("your id didn't work idiot PepeLaugh")
    have_me = False
else:
    have_me = True

if have_emongg:
    emongg_check = twitch_stuff.get_status(emongg_id)
if have_me:
    me_check = twitch_stuff.get_status(me_id)

#Setup finished

client = discord.Client()

#creating filter list
reg_ban_list = regexgen.regexdic
reg_ban_list['twitch'] = r'twitch\.tv/.+'
reg_ban_list['discord'] = r'discord\.gg/.+'


def reg_filter(message, regstring):
    #filter message for specific regex string
    x = re.search(regstring, message)
    if x is None:
        return False
    else:
        return True


def check_live(streamid, live_check):
    #streamid is string
    #live_check is bool
    currentDT = str(datetime.datetime.now())
    try:
        new_check = twitch_stuff.get_status(streamid)
    except:
        logger.exception('message: ')
        return live_check, False
    if new_check:
        if not live_check:
            return new_check, True #(True, True)
        elif live_check:
            logger.info(streamid + ' still live as of ' + currentDT)
            return new_check, False #(True, False)
        else:
            return live_check, False #error
            print('something broke. live_check = ', live_check)
    elif new_check is False:
        if live_check:
            logger.info(streamid + ' offline at ' + currentDT)
            return new_check, True
        logger.info(streamid + ' not live as of ' + currentDT)
        return new_check, False
    else:
        return live_check, False
        print('something broke. new_check = ', new_check)


async def me_ping():
    #if y is true, an action needs to be taken
    #if me_check is true, he was live last check
    #if both y and me_check are true, i am offline
    global me_check
    while True:
        x = check_live(me_id, me_check)
        me_check1 = x[0]
        y = x[1]
        if y and me_check is False:
            currentDT = str(datetime.datetime.now())
            logger.info('posting message at ' + currentDT)
            message = '''@everyone beep boop zambam is live beep boop go call him an idiot beep boop
https://www.twitch.tv/zambam5'''
            channel = client.get_channel(id=511209374883250197)
            await channel.send(message)
            me_check = me_check1
        elif y and me_check is True:
            currentDT = str(datetime.datetime.now())
            logger.info('purging messages at ' + currentDT)
            channel = client.get_channel(id=511209374883250197)
            await channel.purge(limit=100, check=is_me)
            me_check = me_check1
        else:
            me_check = me_check1
        if emongg_check:
            await asyncio.sleep(1800)
        else:
            await asyncio.sleep(600)


async def emongg_ping():
    global emongg_check
    #if y is true, an action needs to be taken
    #if emongg_check is true, he was live last check
    #if both y and emongg_check are true, emongg is offline
    while True:
        x = check_live(emongg_id, emongg_check)
        emongg_check1 = x[0]
        y = x[1]
        if y and emongg_check is False:
            currentDT = str(datetime.datetime.now())
            logger.info('posting message at ' + currentDT)
            message = '''@everyone emongg is live <:FeelsOkayMan:585969133368246308>
https://www.twitch.tv/emongg'''
            channel = client.get_channel(id=611949109854863420)
            await channel.purge(limit=100, check=is_me)
            await channel.send(message)
            emongg_check = emongg_check1
        elif y and emongg_check is True:
            currentDT = str(datetime.datetime.now())
            logger.info('purging messages at ' + currentDT)
            channel = client.get_channel(id=611949109854863420)
            await channel.purge(limit=100, check=is_me)
            message = "Not live <:FeelsStrongMan:585969881003065367>"
            await channel.send(message)
            emongg_check = emongg_check1
        else:
            emongg_check = emongg_check1
        if emongg_check:
            await asyncio.sleep(1800)
        else:
            await asyncio.sleep(60)

async def new_video():
    global latest_id
    global checkedids
    while True:
        currentDT = str(datetime.datetime.now())
        try:
            latestvideo = yt.latestvideo()
        except:
            continue
        check_id = latestvideo[0]
        logger.info(latest_id + " most recent id checked at " + currentDT)
        if check_id in checkedids:
            await asyncio.sleep(90)
        elif check_id != latest_id:
            checkedids.append(check_id)
            youtube = "https://youtu.be/{}".format(check_id)
            message = '''@everyone Emongg has uploaded a new video, go check it out:
{}'''.format(youtube)
            channel = client.get_channel(id=432037025668136975)
            await channel.send(message)
            latest_id = check_id
            await asyncio.sleep(90)
        else:
            await asyncio.sleep(90)


def is_me(m):
    return m.author == client.user


async def pugs(message):
    #TODO: add variables for channel ids
    body = message.content
    bodylist = body.split(" ")
    cmd = bodylist[0]
    if cmd == "~!announce":
        body = " ".join(bodylist[1:])
        commandlist = body.split(", ")
        name = message.author.mention
        region = commandlist[0]
        t = commandlist[1]
        tag = commandlist[2]
        emote = commandlist[3]
        emote2 = emote.strip('<>')
        # emote3 = commandlist[4]
        # emote4 = emote3.strip('<>')
        role = discord.utils.get(message.guild.roles, name="PUGs")
        content = "{} will be hosting {} PUGs at {}. Add {} and react with {} if you're interested. PUGs will run if we get 13 reactions that aren't the bot.".format(name, region, t, tag, emote)
        await role.edit(mentionable=True)
        channel = client.get_channel(id=555380447509610517)
        newmessage = await channel.send(role.mention + " " + content)
        await role.edit(mentionable=False)
        await newmessage.add_reaction(emote2)
        # await newmessage.add_reaction(emote4)
    elif cmd == "~!announceeu":
        body = " ".join(bodylist[1:])
        commandlist = body.split(", ")
        name = message.author.mention
        t = commandlist[1]
        tag = commandlist[2]
        emote = commandlist[3]
        emote2 = emote.strip('<>')
        # emote3 = commandlist[4]
        # emote4 = emote3.strip('<>')
        role = discord.utils.get(message.guild.roles, name="EU")
        content1 = "{} will be hosting ".format(name)
        content2 = " PUGs at {}. Add {} and react with {} if you're interested. PUGs will run if we get 13 reactions that aren't the bot.".format(t, tag, emote)
        await role.edit(mentionable=True)
        channel = client.get_channel(id=555380447509610517)
        newmessage = await channel.send(content1 + role.mention + content2)
        await role.edit(mentionable=False)
        await newmessage.add_reaction(emote2)
        # await newmessage.add_reaction(emote4)
    elif cmd == "~!start":
        name = message.author.mention
        role = discord.utils.get(message.guild.roles, name="PUGs")
        content = "{} is starting PUGs. Make sure you have added the above tag, then choose to spectate lobby. React with <:white_check_mark:602625053284237314> when you join.".format(name)
        await role.edit(mentionable=True)
        channel = client.get_channel(id=555380447509610517)
        newmessage = await channel.send(role.mention + " " + content)
        await role.edit(mentionable=False)
        await newmessage.add_reaction('✅')
    elif cmd == "~!starteu":
        name = message.author.mention
        role = discord.utils.get(message.guild.roles, name="EU")
        content = "{} is starting PUGs. Make sure you have added the above tag, then choose to spectate lobby. React with <:white_check_mark:602625053284237314> when you join.".format(name)
        await role.edit(mentionable=True)
        channel = client.get_channel(id=555380447509610517)
        newmessage = await channel.send(role.mention + " " + content)
        await role.edit(mentionable=False)
        await newmessage.add_reaction('✅')
    elif cmd == "~!pugs":
        name = message.author.mention
        role = discord.utils.get(message.guild.roles, name="PUGs")
        messagelist=message.content.split(" ")
        content = ''.join(word + " " for word in messagelist[1:])
        await role.edit(mentionable=True)
        channel = client.get_channel(id=555380447509610517)
        await channel.send(role.mention + " message from " + name + ": " + content)
        await role.edit(mentionable=False)
    elif cmd == "~!eu":
        name = message.author.mention
        role = discord.utils.get(message.guild.roles, name="EU")
        messagelist=message.content.split(" ")
        content = ''.join(word + " " for word in messagelist[1:])
        await role.edit(mentionable=True)
        channel = client.get_channel(id=555380447509610517)
        await channel.send(role.mention + " message from " + name + ": " + content)
        await role.edit(mentionable=False)
    elif cmd == '~!purge':
        channel = client.get_channel(id=555380447509610517)
        deleted = await channel.purge(limit=100, check=is_me)
        channel2 = client.get_channel(id=527239830678011905)
        await channel2.send('Deleted {} messages'.format(len(deleted)))


async def emongg_msg(message):
    allowedroles = ['EMONGG',
                    'BOTS',
                    'Streamer',
                    'MOD',
                    'DATZRAGE',
                    'EVERGREEN',
                    'Artists'
]
    if message.channel.id == 527239830678011905:
        await pugs(message)
    else:
        await msg_filter(message, allowedroles)


async def msg_filter(message, allowedroles):
    for word in reg_ban_list.keys():
        y = reg_filter(message.content, reg_ban_list[word])
        if y:
            logger.info("found a filter: " + word)
            banned_word = word
            break
    if y:
        if banned_word == 'twitch':
            if "clips.twitch.tv/" in message.content:
                return
            elif "twitch.tv/emongg" in message.content:
                return
            elif message.channel.id == 529760531800915988:
                return
            roles = message.author.roles
            for role in roles:
                if role.name in allowedroles:
                    return
            logger.info('twitch link')
            name = message.author.mention
            await message.delete()
            channel = message.channel
            await channel.send("no twitch links {}".format(name))
        elif banned_word == 'discord':
            roles = message.author.roles
            for role in roles:
                if role.name in allowedroles:
                    return
            logger.info('discord link')
            name = message.author.mention
            await message.delete()
            channel = message.channel
            await channel.send("no discord invites {}".format(name))
        else:
            roles = message.author.roles
            for role in roles:
                if role.name in allowedroles:
                    return
            logger.info('banned')
            guild = message.guild
            await guild.ban(message.author, delete_message_days=1)


time_units = {
            'h': 3600,
            'm': 60,
            's': 1
}
reminder_list=[]

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
            await channel.send('Unit must be hours(h), minutes(m), or seconds(s)')
            return reminders
        reminder = ''.join(word +" " for word in m[3:])
        name = message.author.mention
        seconds = quantity*time_units[unit]
        if seconds >= 1209600:
            await channel.send('That is too far in the future I may be dead <:FeelsStrongMan:585969881003065367>')
            return reminders
        else:
            remindtime = time.time()+seconds
            reminders.append(
                {
                'future': remindtime,
                'author': name,
                'reminder': reminder,
                'channel': channel
                }
            )
            logger.info('reminder added for ' + str(message.author))
            await channel.send(name + " I will remind you in {} seconds".format(seconds))
            return reminders
    else:
        return reminders


async def check_reminders():
    global reminder_list
    while True:
        to_remove = []
        for reminder in reminder_list:
            if reminder['future'] <= time.time():
                await reminder['channel'].send(reminder['author'] + " here is your reminder for " + reminder['reminder'])
                to_remove.append(reminder)
                logger.info('reminder removed')
        if to_remove:
            leftovers = [x for x in reminder_list if x not in to_remove]
            reminder_list = leftovers
        await asyncio.sleep(5)



@client.event
async def on_message(message):
    global reminder_list
    if message.guild.name == "emongg":
        await emongg_msg(message)
    elif message.channel.id == 422170422516121612:
        if message.content.startswith('~!ping'):
            logger.info('ping received')
            channel = message.channel
            try:
                taskset = asyncio.Task.all_tasks(client.loop)
                taskcheck = {}
                for item in taskset:
                    stritem = str(item)
                    if 'emongg_ping()' in stritem:
                        taskcheck['emongg'] = True
                    elif 'me_ping()' in stritem:
                        taskcheck['zam'] = True
                    elif 'new_video()' in stritem:
                        taskcheck['video'] = True
                msg = ''
                if taskcheck.keys() == []:
                    msg = 'no tasks running'
                else:
                    for key in taskcheck.keys():
                        msg += ' ' + key + ' is running'
                await channel.send('beep boop')
                await channel.send(msg)
            except:
                await channel.send('failure :(')
                logger.exception("message: ")
    else:
        await remind_me(message, reminder_list)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you struggle"))
    print("Logged in as " + client.user.name)

'''@client.event
async def on_message_delete(message):
    logger.info('message deleted')
    guild = message.guild.name
    if guild != "emongg":
        return
    name = message.author.name
    if name == 'zambot':
        return
    userid = message.author.id
    pfp = message.author.avatar_url
    content = message.content
    channel = message.channel.name
    if channel == "admin-stuff":
        return
    att = message.attachments
    pic = False
    if att != []:
        pic = True
        picurl = att[0]['url']
    if pic:
        embed = discord.Embed(title="Message deleted in #{}".format(channel), colour=discord.Colour(0x8e00f6), description="{}".format(content))
        embed.set_author(name="{}".format(name), icon_url="{}".format(pfp))
        embed.set_footer(text="ID: {}".format(userid))
        embed.add_field(name="Image", value="{}".format(picurl))
        channel2 = client.get_channel(id=544928115202195487)
        await channel2.send(embed=embed)
    else:
        embed = discord.Embed(title="Message deleted in #{}".format(channel), colour=discord.Colour(0x8e00f6), description="{}".format(content))
        embed.set_author(name="{}".format(name), icon_url="{}".format(pfp))
        embed.set_footer(text="ID: {}".format(userid))
        channel2 = client.get_channel(id=544928115202195487)
        await channel2.send(embed=embed)'''

try:
    client.loop.create_task(new_video())
    client.loop.create_task(check_reminders())
    if have_emongg:
        print('creating loop for emongg')
        client.loop.create_task(emongg_ping())
    if have_me:
        print('creating loop for me')
        client.loop.create_task(me_ping())
    client.run(TOKEN)
except:
    logger.exception("message:")
