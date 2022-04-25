import discord
import time
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import os

load_dotenv()


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.slash_command(name="help", description="List all / commands and their uses")
    async def help(self, ctx: Context):
        embed = discord.Embed(title="Commands:", color=discord.Color.blue())
        embed.add_field(name="/create_giveaway", value="Creates a giveaway with a specified prize and time, and selects a winner randomly when the time is up.\n", inline=False)
        embed.add_field(name="/poll", value="desc\n", inline=False)
        embed.add_field(name="/opensea", value="desc\n", inline=False)
        embed.add_field(name="/reaction_roles", value="desc\n", inline=False)
        embed.add_field(name="/add_to_blacklist", value="desc\n", inline=False)
        embed.add_field(name="/get_blacklist", value="desc\n", inline=False)
        embed.add_field(name="/remove_from_blacklist", value="desc\n", inline=False)
        embed.add_field(name="/record", value="desc\n", inline=False)
        embed.add_field(name="/getrecord", value="desc\n", inline=False)
        embed.add_field(name="/setup", value="desc\n", inline=False)
        return await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))