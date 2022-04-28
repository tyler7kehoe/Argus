from asyncio import sleep
from cgi import print_exception
import datetime
import json
import os
from traceback import print_exc
import discord
from discord.ext import commands, tasks
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import requests
from dateutil import parser

load_dotenv()
 
class Opensea_task(commands.Cog):
    headers = {
            "Accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_KEY")
        }
    
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.printer.start()
        

    def cog_unload(self):
        self.printer.cancel()


    @tasks.loop(seconds=15.0)
    async def printer(self):
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
        for guild in data:
            gu_id = guild['guild_id']
            guild_obj = self.bot.get_guild(gu_id)
            contracts = guild['contracts']

            for contract in contracts:
                chid = contract['channel_id']
                ch = guild_obj.get_channel(chid)
                contract_address = contract['contract_address']
                time = parser.parse(contract['time'])

                params = {
                "only_opensea": 'true',            
                'asset_contract_address': contract_address,
                "event_type": 'successful',
                "occurred_after": time
                }
                await sleep(1)
                addr = requests.get("https://api.opensea.io/api/v1/events?event_type=successful", params=params, headers=self.headers)
                contract['time'] = str(datetime.datetime.utcnow())
                addr = addr.json()
                addr = addr['asset_events']

                for i in range(len(addr)):
                    title = addr[i]['asset']['name']
                    description = addr[i]['asset']['asset_contract']["name"]
                    img = addr[i]['asset']['image_url']
                    from_acc = addr[i]['transaction']['from_account']['address']
                    to_acc = addr[i]['winner_account']['address']

                    embed = discord.Embed(title=f"{title}", color=discord.Color.blue(),
                                    description=f'{description}')
                    embed.add_field(name='Seller:', value=f'[{from_acc[:-35]}](https://etherscan.io/address/{from_acc})')
                    embed.add_field(name='Buyer:', value=f'[{to_acc[:-35]}](https://etherscan.io/address/{to_acc})')     # trouble reaching buyer location with indexing.
                    embed.timestamp = datetime.datetime.now()
                    embed.set_image(url=img)
                    await ch.send(embed=embed)

        with open("data/opensea.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)


    @printer.before_loop
    async def before_printer(self):
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
        for guild in data:
            contracts = guild['contracts']
            for contract in contracts:
                contract['time'] = str(datetime.datetime.utcnow())
        with open("data/opensea.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)
        await self.bot.wait_until_ready()
        

def setup(bot):
    bot.add_cog(Opensea_task(bot))