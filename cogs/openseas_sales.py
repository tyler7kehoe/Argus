import discord
import os
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

load_dotenv()


class openseas_sales(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot


def setup(bot):
    bot.add_cog(openseas_sales(bot))

