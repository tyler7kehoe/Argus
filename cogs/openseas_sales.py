import discord
import os
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

load_dotenv()


class openseas_sales(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="opensea",
                            description="Automatically post opensea sales in an embed",
                            guild_ids=[int(os.getenv("GUILD_ID"))])
    async def opensea(self, ctx: Context, channel, contract_address):
        def check(m):
            return m.content and m.channel == ctx.channel
        
        print("TESTTESTEST")
        if channel == None or contract_address == None:
            return await ctx.send('Usage: gcreate {channel name} {contract address}')
        print(channel)
        ch = self.bot.get_channel(int(channel[2:-1]))
        await ctx.respond(ch)

def setup(bot):
    bot.add_cog(openseas_sales(bot))
