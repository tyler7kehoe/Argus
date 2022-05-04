import datetime
import json
import discord
from discord.ext import commands, tasks
from discord.ext.commands.context import Context
from dotenv import load_dotenv

load_dotenv()
global task_schedule

class Openseas_Sales(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="opensea",
                            description="Automatically post opensea sales in an embed")
    async def opensea(self, ctx: Context, channel, contract_address):
        ch = self.bot.get_channel(int(channel[2:-1]))
        guild_id = ctx.guild.id
    
        if(self.log_contract_tracker(guild_id, ch.id, contract_address)):
            await ctx.respond('Transactions from this contract will now be tracked.')
        else:
            await ctx.respond("This contract is already being tracked in this channel.")

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="opensea_remove_contract",
                            description="Remove a contract from being tracked")
    async def opensea_remove(self, ctx: Context, contract_address):
        guild_id = ctx.guild.id
        found = False
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            for item in data:
                if item['guild_id'] == guild_id:
                    for contract in item['contracts']:
                        if contract['contract_address'] == contract_address:
                            item['contracts'].remove(contract)
                            await ctx.respond(f'Contract: {contract_address} removed')
                            found = True
        with open("data/opensea.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)
        if not found:
            ctx.respond(f'Contract: {contract_address} not found')



    def log_contract_tracker(self, guild_id, channel_id, contract_address):
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            for i in range(len(data)):
                if guild_id == data[i]['guild_id']:
                    break
            else:
                i = len(data)
                data.append({'guild_id': guild_id, 'contracts': []})
            new_set = {
                'channel_id': channel_id,
                'contract_address': contract_address,
                'time': str(datetime.datetime.utcnow()),
                'lastId': -1
                            }
            for j in range(len(data[i]['contracts'])):
                if new_set['channel_id'] == data[i]['contracts'][j]['channel_id'] \
                and new_set['contract_address'] == data[i]['contracts'][j]['contract_address']:
                    newdata = False
                    break
            else:
                data[i]['contracts'].append(new_set)
                newdata = True
           
        with open("data/opensea.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)
        return newdata


def setup(bot):
    bot.add_cog(Openseas_Sales(bot))


