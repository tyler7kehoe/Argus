from re import L
from discord import Option
from discord.ext import commands
from discord.ext.commands.context import Context
from api import embed_builder

import os
from dotenv import load_dotenv

from api.data_handler import *

load_dotenv()

class Set(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="record",description="Input a record into the database!", guild_ids=[int(os.getenv("GUILD_ID"))])
    async def record(self, ctx: Context,
        content:Option(str, "The text you want recorded.",required=True)
    ):
        await ctx.defer(ephemeral=True)
        await set_input(ctx.author.id, content)
        await ctx.respond(embed=embed_builder.embed_builder("Wallet Recorded", ctx.author, f"```{content}```", embed_builder.embed_color.NEUTRAL, "Created by DabMan"),ephemeral=True)

def setup(bot):
    bot.add_cog(Set(bot))