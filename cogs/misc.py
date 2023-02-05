import setuptools
import json
import os
import logging
import asyncio
import datetime
import time
from discord import utils
from discord import ActivityType

from discord.ext import tasks, commands
import discord
from setuptools import Command

logger = logging.getLogger("__main__." + __name__)


def check_if_it_is_me(ctx):
    return ctx.message.author.id == 297516831227510786


class Misc(commands.Cog):
    def __init__(self, bot, ping_config, voice_config):
        self.bot = bot
        self.ping_config = ping_config
        self.voice_config = self.config_parser(voice_config)

    @staticmethod
    def config_parser(config):
        d = dict()
        for key in config.keys():
            d[int(key)] = config[key]
        return d

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild2 = after.channel.guild.id
        if guild2 not in self.voice_config.keys():
            return
        name = member.name
        pfp = member.display_avatar
        userid = member.id
        # guild1 = before.channel.guild.id

        try:
            if before.channel == None and after.channel is not None:
                embed = discord.Embed(
                    title=None,
                    colour=discord.Colour(0x8E00F6),
                    description=f"**{member.mention} joined voice channel {after.channel.mention}**",
                    timestamp=datetime.datetime.utcfromtimestamp(time.time()),
                )
                embed.set_author(name="{}".format(name), icon_url="{}".format(pfp))
                embed.set_footer(text="ID: {}".format(userid))
                channel2 = self.bot.get_channel(self.voice_config[guild2])
                await channel2.send(embed=embed)
            elif (
                before.channel is not None
                and after.channel is not None
                and before.channel != after.channel
            ):
                embed = discord.Embed(
                    title=None,
                    colour=discord.Colour(0x8E00F6),
                    description=f"**{member.mention} switched voice channel {before.channel.mention} -> {after.channel.mention}**",
                    timestamp=datetime.datetime.utcfromtimestamp(time.time()),
                )
                embed.set_author(name="{}".format(name), icon_url="{}".format(pfp))
                embed.set_footer(text="ID: {}".format(userid))
                channel2 = self.bot.get_channel(self.voice_config[guild2])
                await channel2.send(embed=embed)
        except:
            return

    @commands.hybrid_command(name="ping")
    @commands.has_guild_permissions(administrator=True)
    # @commands.check(check_if_it_is_me)
    async def _ping(self, ctx):
        if ctx.message.guild.name not in self.ping_config.keys():
            return
        guild = ctx.message.guild
        if ctx.message.channel.id == self.ping_config[guild.name]:
            logger.info("ping received")
            # channel = ctx.message.channel
            try:
                taskset = asyncio.all_tasks(self.bot.loop)
                await ctx.send("beep boop")
                await ctx.send("I am running " + str(len(taskset)) + " tasks")
            except:
                await ctx.send("failure :(")
                logger.exception("message: ")

    @commands.command(name="sync")
    @commands.has_guild_permissions(administrator=True)
    async def _sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Sync attempted")

    @commands.command(name="reset_slash_commands")
    @commands.has_guild_permissions(administrator=True)
    async def _reset(self, ctx):
        return


if os.path.isfile("./config/config-test.json"):
    with open("./config/config-test.json", "r") as f:
        config = json.load(f)

ping_config = config["MISC"]["PING"]
voice_config = config["MISC"]["VOICE_LOG"]


async def setup(bot):
    await bot.add_cog(Misc(bot, ping_config, voice_config))
