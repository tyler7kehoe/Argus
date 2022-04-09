import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    #TODO: Listen for member join/nick name change to copy of mods/blacklisted names



def setup(bot):
    bot.add_cog(Moderation(bot))
