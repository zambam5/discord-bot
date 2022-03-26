from ast import alias
import aiohttp, json, datetime, logging, asyncio, time, os, random
from discord.ext import tasks, commands
from setuptools import Command
import discord


logger = logging.getLogger("__main__." + __name__)


class TwitchCommands(commands.Cog):
    '''def __init__(self, discord):
    """Constructor for the DiscordNotif class

    Args:
        discord (class): Discord client object
        ID (str): Twitch API ID
        token (str): OAuth token corresponding to the ID for the Twitch API
    """
    self.discord = discord
    self.configpath = "config/twitch.json"
    self.process_config(self.configpath)'''

    def process_config(self, configpath: str):
        # TODO add section to config for server
        if os.path.isfile(configpath):
            # check for existing config file
            with open(configpath, "r") as f:
                r = json.load(f)
            self.ID = r["ID"]
            self.TOKEN = r["TOKEN"]
            self.secret = r["SECRET"]
            self.default = r["DEFAULT_ERROR"]
            self.notifications = r["NOTIFICATIONS"]
            self.path = r["PATH"]
            self.status = None
        # figure out what to do if no config file
        else:
            with open(configpath, "w"):
                f.write(json.dumps({}))

    def is_me(self, m):
        """Function to check if the user is the bot

        Args:
            m (class): Message object from the Discord module

        Returns:
            bool: True or False depending on if the user is the bot
        """
        return m.author == self.discord.user

    def update_config(self):
        logger.info("updating twitch config")
        with open(self.configpath, "r") as f:
            r = json.load(f)
        r["NOTIFICATIONS"] = self.notifications
        with open(self.configpath, "w") as f:
            f.write(json.dumps(r))

    @commands.has_role("Admin")  # TODO Change this to be a function based on server
    @commands.group()
    async def twitch(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use !twitch help for how to use this command")

    @twitch.group()
    async def update(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use !twitch help for how to use this command")

    @update.group()
    async def message(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use !twitch help for how to use this command")

    @message.command()
    async def remove(self, ctx, channel, message_type, message):
        logger.info("removing message from %s", channel)
        messages = self.notifications[channel][message_type]["messages"]
        new_messages = [x for x in messages if x != messages[message]]
        print(new_messages)
        self.notifications[channel][message_type]["messages"] = new_messages
        print(self.notifications[channel][message_type]["messages"])
        self.update_config()
        await ctx.send(f"Updated messages for {channel}")

    @message.command()
    async def add(self, ctx, channel, message_type, message):
        self.notifications[channel][message_type]["messages"].append(message)
        self.update_config()
        logger.info("added message to %s", channel)
        await ctx.send(f"Updated messages for {channel}")

    @update.group()
    async def cd(self, ctx, channel, type, amount):
        self.notifications[channel]["cd"][type] = int(amount)
        logger.info("Updating %s cooldown for %s", type, channel)
        self.update_config()
        await ctx.send(f"Updated {type} cooldown for {channel}")

    @update.command()
    async def settings(self, ctx, channel):
        embed = discord.Embed(
            title=f"{channel} settings", colour=discord.Colour(0xF15F3E)
        )
        if not self.notifications[channel]["ping"]["custom"][0]:
            embed.add_field(
                name="Ping",
                value=f"The ping messages are:\r\n "
                + "\r\n".join(self.notifications[channel]["ping"]["messages"])
                + f"\r\n The ping channel has id {self.notifications[channel]['ping']['channel']}",
                inline=False,
            )
        elif self.notifications[channel]["ping"]["custom"][1]["embed"]:
            embed.add_field(
                name="Ping",
                value=f"The ping messages are:\r\n "
                + "\r\n".join(self.notifications[channel]["ping"]["messages"])
                + f"\r\n The ping channel has id {self.notifications[channel]['ping']['channel']}.\r\n"
                + "There will be a custom mesage with an embed on the next ping",
                inline=False,
            )
        else:
            embed.add_field(
                name="Ping",
                value=f"The ping messages are:\r\n "
                + "\r\n".join(self.notifications[channel]["ping"]["messages"])
                + f"\r\n The ping channel has id {self.notifications[channel]['ping']['channel']}.\r\n"
                + "There will be a custom mesage on the next ping",
                inline=False,
            )
        if not self.notifications[channel]["offline"]["messages"]:
            embed.add_field(
                name="Offline",
                value="This channel has no offline message",
                inline=False,
            )
        else:
            embed.add_field(
                name="Offline",
                value=f"The offline messages are:\r\n "
                + "\r\n".join(self.notifications[channel]["offline"]["messages"])
                + f"\r\n The offline channel has id {self.notifications[channel]['offline']['channel']}",
                inline=False,
            )
        embed.add_field(
            name="Game",
            value=f"The game change message is:\r\n "
            + self.notifications[channel]["game"]["messages"]
            + f"\r\n The game channel has id {self.notifications[channel]['game']['channel']}",
            inline=False,
        )
        embed.add_field(
            name="Cooldowns",
            value=f"The cooldown periods for the bot to update stream status are:\r\n"
            + "\r\n".join(
                [
                    x + ": " + str(self.notifications[channel]["cd"][x])
                    for x in self.notifications[channel]["cd"].keys()
                ]
            ),
        )
        await ctx.send(embed=embed)

    @twitch.command()
    async def custommessage(self, ctx, channel, message):
        self.notifications[channel]["ping"]["custom"] = [True]
        x = dict()
        x["embed"] = False
        x["message"] = message
        self.notifications[channel]["ping"]["custom"].append(x)
        logger.info("Adding custom ping to %s", channel)
        self.update_config()
        await ctx.send(
            f"Custom message added for {channel}. It will trigger the next time the stream goes live."
        )

    @twitch.command()
    async def customembed(self, ctx, channel, message, link, title, url=None):
        """"""
        self.notifications[channel]["ping"]["custom"] = [True]
        x = dict()
        x["embed"] = True
        x["message"] = message
        x["link"] = link
        x["title"] = title
        x["url"] = url
        self.notifications[channel]["ping"]["custom"].append(x)
        await ctx.send(f"Custom embed set for {channel}")
        logger.info("Adding custom ping with embed to %s", channel)
        self.update_config()

    @twitch.command()
    async def test(self, ctx, username):
        logger.info("Requested to post test message for %s", username)
        user_info = self.notifications[username]["ping"]
        game = "Test"
        role = user_info["role"]
        if role == user_info["guild"]:
            mention = "@everyone"
        else:
            g = self.discord.get_guild(id=user_info["guild"])
            mention = g.get_role(role_id=role).mention
        if not user_info["custom"][0]:
            ping_list = user_info["messages"]
            message = mention + " " + random.choice(ping_list).format(game)
            await ctx.send(message)
        elif user_info["custom"][1]["embed"]:
            message_d = user_info["custom"][1]
            message = mention + " " + message_d["message"]
            title = message_d["title"]
            link = message_d["link"]
            if message_d["url"]:
                embed = discord.Embed(
                    title=title,
                    color=discord.Colour.purple(),
                    url=message_d["url"],
                    description=f"[Click here to watch stream](https://twitch.tv/{username})",
                )
                embed.set_image(url=link)
                await ctx.send(message, embed=embed)
            else:
                embed = discord.Embed(
                    title=title,
                    color=discord.Colour.purple(),
                    url=f"https://twitch.tv/{username}",
                    description=f"[Click here to watch stream](https://twitch.tv/{username})",
                )
                embed.set_image(url=link)
                await ctx.send(message, embed=embed)
        else:
            message = mention + " " + user_info["custom"][1]["message"]
            await ctx.send(message)
