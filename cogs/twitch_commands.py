import aiohttp, json, datetime, logging, asyncio, time, os, random
from discord.ext import tasks, commands
from setuptools import Command
import discord


logger = logging.getLogger("__main__." + __name__)


class TwitchCommands(commands.Cog):
    def is_me(self, m):
        """Function to check if the user is the bot

        Args:
            m (class): Message object from the Discord module

        Returns:
            bool: True or False depending on if the user is the bot
        """
        return m.author == self.discord.user

    def update_config(self, channel):
        logger.info("updating twitch config for %s", channel)
        with open(self.configpath, "r") as f:
            r = json.load(f)
        r["NOTIFICATIONS"][channel] = self.streams[channel].create_dict()
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
        self.streams[channel].update_messages(message, message_type, remove=True)
        self.update_config(channel)
        await ctx.send(f"Updated messages for {channel}")

    @message.command()
    async def add(self, ctx, channel, message_type, message):
        self.streams[channel].update_messages(message, message_type, add=True)
        self.update_config(channel)
        logger.info("added message to %s", channel)
        await ctx.send(f"Updated messages for {channel}")

    @update.group()
    async def cd(self, ctx, channel, type, amount):
        self.streams[channel].update_cd(type, amount)
        logger.info("Updating %s cooldown for %s", type, channel)
        self.update_config(channel)
        await ctx.send(f"Updated {type} cooldown for {channel}")

    @update.command()
    async def settings(self, ctx, channel):
        # TODO This function also wants the dict from streams.py
        notifications = self.streams[channel].create_dict()
        embed = discord.Embed(
            title=f"{channel} settings", colour=discord.Colour(0xF15F3E)
        )
        if not notifications["ping"]["custom"][0]:
            embed.add_field(
                name="Ping",
                value=f"The ping messages are:\r\n "
                + "\r\n".join(notifications["ping"]["messages"])
                + f"\r\n The ping channel has id {notifications['ping']['channel']}",
                inline=False,
            )
        elif notifications["ping"]["custom"][1]["embed"]:
            embed.add_field(
                name="Ping",
                value=f"The ping messages are:\r\n "
                + "\r\n".join(notifications["ping"]["messages"])
                + f"\r\n The ping channel has id {notifications['ping']['channel']}.\r\n"
                + "There will be a custom mesage with an embed on the next ping",
                inline=False,
            )
        else:
            embed.add_field(
                name="Ping",
                value=f"The ping messages are:\r\n "
                + "\r\n".join(notifications["ping"]["messages"])
                + f"\r\n The ping channel has id {notifications['ping']['channel']}.\r\n"
                + "There will be a custom mesage on the next ping",
                inline=False,
            )
        if not notifications["offline"]["messages"]:
            embed.add_field(
                name="Offline",
                value="This channel has no offline message",
                inline=False,
            )
        else:
            embed.add_field(
                name="Offline",
                value=f"The offline messages are:\r\n "
                + "\r\n".join(notifications["offline"]["messages"])
                + f"\r\n The offline channel has id {notifications['offline']['channel']}",
                inline=False,
            )
        embed.add_field(
            name="Game",
            value=f"The game change message is:\r\n "
            + notifications["game"]["messages"]
            + f"\r\n The game channel has id {notifications['game']['channel']}",
            inline=False,
        )
        embed.add_field(
            name="Cooldowns",
            value=f"The cooldown periods for the bot to update stream status are:\r\n"
            + "\r\n".join(
                [
                    x + ": " + str(notifications["cd"][x])
                    for x in notifications["cd"].keys()
                ]
            ),
        )
        await ctx.send(embed=embed)

    @twitch.command()
    async def custommessage(self, ctx, channel, message):
        embed = False
        self.streams[channel].add_custom_message(message, embed)
        logger.info("Adding custom ping to %s", channel)
        self.update_config(channel)
        await ctx.send(
            f"Custom message added for {channel}. It will trigger the next time the stream goes live."
        )

    @twitch.command()
    async def customembed(self, ctx, channel, message, link, title, url=None):
        """"""
        embed = True
        self.streams[channel].add_custom_message(message, embed, link, title, url)
        await ctx.send(f"Custom embed set for {channel}")
        logger.info("Adding custom ping with embed to %s", channel)
        self.update_config(channel)

    @twitch.command()
    async def test(self, ctx, username):
        logger.info("Requested to post test message for %s", username)
        user_info = self.streams[username].ping
        game = "Test"
        role = user_info["role"]
        if role == user_info["guild"]:
            mention = "@everyone"
        else:
            g = self.discord.get_guild(user_info["guild"])
            mention = g.get_role(role).mention
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
