import setuptools
import json
import os
import logging
import asyncio
import datetime
from discord import utils
from discord import ActivityType

from discord.ext import tasks, commands
import discord
from setuptools import Command

logger = logging.getLogger("__main__." + __name__)


def check_if_it_is_me(ctx):
    return ctx.message.author.id == 297516831227510786


class Misc(commands.Cog):
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        logger.info("test")
        name = member.name
        pfp = member.avatar_url
        userid = member.id
        # guild1 = before.channel.guild.id
        try:
            guild2 = after.channel.guild.id
            print(guild2)
            if guild2 != 110671202594373632:
                return
            if before.channel == None and after.channel is not None:
                embed = discord.Embed(
                    colour=discord.Colour(0x8E00F6),
                    description=f"**{member.mention} joined voice channel {after.channel.mention}**",
                    timestamp=datetime.datetime.utcfromtimestamp(1551994754),
                )
                embed.set_author(name="{}".format(name), icon_url="{}".format(pfp))
                embed.set_footer(text="ID: {}".format(userid))
                channel2 = self.bot.get_channel(id=550385977663815690)
                await channel2.send(embed=embed)
            elif (
                before.channel is not None
                and after.channel is not None
                and before.channel != after.channel
            ):
                embed = discord.Embed(
                    colour=discord.Colour(0x8E00F6),
                    description=f"**{member.mention} switched voice channel {before.channel.mention} -> {after.channel.mention}**",
                    timestamp=datetime.datetime.utcfromtimestamp(1551994754),
                )
                embed.set_author(name="{}".format(name), icon_url="{}".format(pfp))
                embed.set_footer(text="ID: {}".format(userid))
                channel2 = self.bot.get_channel(id=550385977663815690)
                await channel2.send(embed=embed)
        except:
            return

    @commands.command(name="ping")
    # @commands.check(check_if_it_is_me)
    async def _ping(self, ctx):
        logger.info("we got here")
        if ctx.message.channel.id == self.channel:
            logger.info("ping received")
            # channel = ctx.message.channel
            try:
                taskset = asyncio.all_tasks(self.bot.loop)
                tasklist = []
                print(tasklist)
                await ctx.send("beep boop")
                await ctx.send("I am running " + str(len(taskset)) + " tasks")
            except:
                await ctx.send("failure :(")
                logger.exception("message: ")


if os.path.isfile("./config/config.json"):
    with open("./config/config.json", "r") as f:
        config = json.load(f)

r_config = config["MISC"]["PING"]


def setup(bot):
    bot.add_cog(Misc(bot, r_config["channel"]))
