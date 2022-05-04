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
                
        embed.add_field(name="/setup", value="For use on a blank server, will automatically create channels and roles based on a template.\n", inline=False)

        embed.add_field(name="/create_giveaway", value="Creates a giveaway with a specified prize and time, and selects a winner randomly when the time is up.\n", inline=False)
        
        embed.add_field(name="/reroll", value="Reroll a previously created giveaway for a number of winners.\n", inline=False)
        
        embed.add_field(name="/poll", value="Creates a poll with a max of 10 options that ends at a specified time.\n", inline=False)
        
        embed.add_field(name="/opensea", value="Given a channel and contact address, will automatically post OpenSea sales in embeds.\n", inline=False)
        
        embed.add_field(name="/opensea_remove_contract", value="Removes a contract that you no longer want tracked.\n", inline=False)

        embed.add_field(name="/reaction_roles", value="Creates an embed so that when users react with given emojis, they will be assigned a corresponding role.\n", inline=False)
        
        embed.add_field(name="/get_blacklist", value="Displays a list of users currently blacklisted from the server.\n", inline=False)

        embed.add_field(name="/add_to_blacklist", value="Adds a user to the blacklist.\n", inline=False)
        
        embed.add_field(name="/remove_from_blacklist", value="Removes a user from the blacklist.\n", inline=False)
        
        embed.add_field(name="/record", value="Records the wallet address for a user.\n", inline=False)
        
        embed.add_field(name="/getrecord", value="Gets the wallet address for a user.\n", inline=False)

        embed.add_field(name="/whitelist", value="Calls button for whitelist members to enter their whitelist address.\n"
                                                 "If button stops working, please reuse command.", inline=False)

        embed.add_field(name="/get_whitelist", value="Sends a CSV file containing all whitelist addresses.\n", inline=False)

        return await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))