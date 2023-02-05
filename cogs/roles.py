import aiohttp, json, datetime, logging, asyncio, time, os, random
from discord.ext import tasks, commands
from setuptools import Command
import discord

logger = logging.getLogger("__main__." + __name__)


class RoleCommand(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def copy(self, ctx, original, new=None):
        guild = ctx.guild
        original_r = guild.get_role(int(original))
        if new:
            new_r = await guild.create_role(
                name=new,
                permissions=original_r.permissions,
                colour=original_r.color,
                hoist=original_r.hoist,
                mentionable=original_r.mentionable,
                reason="Copying role " + original,
            )
            await ctx.send("Role created")
        else:
            new_r = await guild.create_role(
                name=original_r.name,
                permissions=original_r.permissions,
                colour=original_r.color,
                hoist=original_r.hoist,
                mentionable=original_r.mentionable,
                reason="Copying role " + original,
            )
            await ctx.send("Role created")
        for category in guild.categories:
            overwrites = category.overwrites_for(original_r)
            await category.set_permissions(new_r, overwrite=overwrites)
            for channel in category.text_channels:
                overwrites = channel.overwrites_for(original_r)
                await channel.set_permissions(target=new_r, overwrite=overwrites)
        await ctx.send("Overwrites added")

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def paste(self, ctx, old, new):
        guild = ctx.guild
        old_r = guild.get_role(int(old))
        new_r = guild.get_role(int(new))
        await new_r.edit(
            name=old_r.name,
            permissions=old_r.permissions,
            colour=old_r.colour,
            hoist=old_r.hoist,
        )
        await ctx.send("Role updated")
        for category in guild.categories:
            overwrites = category.overwrites_for(old_r)
            await category.set_permissions(new_r, overwrite=overwrites)
            for channel in category.text_channels:
                overwrites = channel.overwrites_for(old_r)
                await channel.set_permissions(target=new_r, overwrite=overwrites)
        await ctx.send("Overwrites added")


async def setup(bot):
    logger.info("Role command loaded")
    await bot.add_cog(RoleCommand(bot))
