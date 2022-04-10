import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

load_dotenv()

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot


def setup(bot):
    bot.add_cog(Games(bot))