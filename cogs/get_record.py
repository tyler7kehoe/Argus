from re import L
from discord import Member, Option
from discord.ext import commands
from discord.ext.commands.context import Context
from api import embed_builder

import os
from dotenv import load_dotenv

from api.data_handler import *

load_dotenv()

class Get(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="getrecord",description="Read an input from the database!")
    async def getrecord(self, ctx: Context,
        user:Option(Member, "The member with the input you want to pull.", required=True)
    ):
        await ctx.defer(ephemeral=True)
        
        if ctx.author.get_role(int(os.getenv("STAFF_ROLE"))) is None:
            await ctx.respond("You may not see this as you aren't staff",ephemeral=True)
        else:
            content = await get_input(user.id)
            await ctx.respond(embed=embed_builder.embed_builder(f"Wallet: {user.name}", ctx.author, f"```{content}```", embed_builder.embed_color.NEUTRAL),ephemeral=True)

def setup(bot):
    bot.add_cog(Get(bot))
