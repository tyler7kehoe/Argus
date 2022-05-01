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
from dateutil.tz import tzlocal
import time as t


load_dotenv()
# TODO its posting duplicates - fix id check thing

 
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


    @tasks.loop(seconds=360)
    async def printer(self):
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
        for guild in data:
            gu_id = guild['guild_id']
            guild_obj = self.bot.get_guild(gu_id)
            contracts = guild['contracts']
            print()
            print("Time 1 then 2:")
            for contract in contracts:
                chid = contract['channel_id']
                ch = guild_obj.get_channel(chid)
                contract_address = contract['contract_address']
                await sleep(1)

                time = parser.parse(contract['time'])
                params = {
                "only_opensea": 'true',            
                'asset_contract_address': contract_address,
                "event_type": 'successful',
                "occurred_after": time - datetime.timedelta(seconds=180)
                } 
                newtime = str(datetime.datetime.utcnow())
                print(time)  
                print(newtime)     
                print()       
                addr = requests.get("https://api.opensea.io/api/v1/events?event_type=successful", params=params, headers=self.headers)
                while addr.status_code == 503:
                    addr = requests.get("https://api.opensea.io/api/v1/events?event_type=successful", params=params, headers=self.headers)
                    print("error 503")

                contract['time'] = newtime

                # print(addr)
                addr = addr.json()
                # print(addr)

                addr = addr['asset_events']
                
                index = 1
                for i in range(len(addr)-1, -1, -1):
                    index += 1
                    print(addr[i]['id'])
                    print(contract['lastId'])
                    if addr[i]['id'] == contract['lastId']:
                        print("yes")
                        break
                    if i == 0:
                        index = 1


                for i in range(len(addr)-index, -1, -1):
                    title = addr[i]['asset']['name']
                    description = addr[i]['asset']['asset_contract']["name"]
                    img = addr[i]['asset']['image_url']
                    from_acc = addr[i]['transaction']['from_account']['address']
                    to_acc = addr[i]['winner_account']['address']

                    embed = discord.Embed(title=f"{title}", color=discord.Color.blue(),
                                    description=f'{description}')
                    embed.add_field(name='Seller:', value=f'[{from_acc[:-35]}](https://etherscan.io/address/{from_acc})')
                    embed.add_field(name='Buyer:', value=f'[{to_acc[:-35]}](https://etherscan.io/address/{to_acc})')     # trouble reaching buyer location with indexing.
                    # embed.timestamp = datetime.datetime.now()
                    timestamp = parser.parse(addr[i]["event_timestamp"])
                    # offset = datetime.datetime.fromtimestamp(timestamp) - datetime.datetime.utcfromtimestamp(timestamp)
                    now = t.time()
                    offset = datetime.datetime.fromtimestamp(now) - datetime.datetime.utcfromtimestamp(now)
                    saletime = timestamp + offset
                    # embed.timestamp = parser.parse(addr[i]["event_timestamp"]).astimezone(tzlocal())
                    embed.timestamp = saletime
                    embed.set_image(url=img)
                    await ch.send(embed=embed)
                if len(addr) > 0:
                    contract['lastId'] = addr[0]['id']


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