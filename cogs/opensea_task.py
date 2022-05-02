from asyncio import sleep
import datetime
import json
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import requests
from dateutil import parser
import time as t


load_dotenv()

 
class Opensea_task(commands.Cog):
    headers = {
            "Accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_KEY")
        }
    
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.check_for_sales.start()
        

    def cog_unload(self):
        self.check_for_sales.cancel()


    @tasks.loop(seconds=15)
    async def check_for_sales(self):
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
                await sleep(1)

                time = parser.parse(contract['time'])
                params = {
                "only_opensea": 'true',            
                'asset_contract_address': contract_address,
                "event_type": 'successful',
                "occurred_after": time - datetime.timedelta(seconds=180)
                } 
                newtime = str(datetime.datetime.utcnow())
                  
                addr = requests.get("https://api.opensea.io/api/v1/events?event_type=successful", params=params, headers=self.headers)
                count = 0
                while addr.status_code == 503:
                    addr = requests.get("https://api.opensea.io/api/v1/events?event_type=successful", params=params, headers=self.headers)
                    count += 1
                    if count > 5:
                        break

                contract['time'] = newtime
                addr = addr.json()
                addr = addr['asset_events']
                
                index = 1
                for i in range(len(addr)-1, -1, -1):
                    index += 1
                    if addr[i]['id'] == contract['lastId']:
                        break
                    if i == 0:
                        index = 1

                for i in range(len(addr)-index, -1, -1):
                    title = addr[i]['asset']['name']
                    description = addr[i]['asset']['asset_contract']["name"]
                    img = addr[i]['asset']['image_url']
                    seller = addr[i]['seller']['address']
                    buyer = addr[i]['winner_account']['address']
                    permalink = addr[i]['asset']['permalink']

                    # get the floor price of the current collection
                    slug = addr[i]['asset']['collection']['slug']
                    url = f"https://api.opensea.io/api/v1/collection/{slug}/stats"
                    headers = {"Accept": "application/json"}
                    get_fp = requests.get(url, headers=headers)
                    get_fp = get_fp.json()
                    fp = get_fp['stats']['floor_price']
                    if len(str(fp)) > 10:
                        fp = str(fp)[:3]

                    # Following block of code converts long num into price of given payment token
                    price_before_calc = addr[i]["total_price"]
                    decimals = addr[i]["payment_token"]["decimals"]
                    temp_list = list(str(price_before_calc).strip(" "))
                    loc = len(temp_list)
                    for num in range(decimals + 1):
                        if num == decimals:
                            temp_list.insert(loc, ".")
                        loc -= 1
                    final_price = ''.join([str(item) for item in temp_list])
                    final_price = final_price.rstrip('0')
                    if final_price.endswith('.'):
                        final_price += '0'
                    price = f'{final_price} {addr[i]["payment_token"]["symbol"]}'

                    embed = discord.Embed(title=f"**New Sale!**", color=discord.Color.random(),
                                          description=f'{title} | [{description}]({permalink})')
                    embed.add_field(name=':moneybag: Seller:', value=f'[{seller[:-35]}](https://etherscan.io/address/{seller})')
                    embed.add_field(name=':shopping_cart: Buyer:', value=f'[{buyer[:-35]}](https://etherscan.io/address/{buyer})')
                    embed.add_field(name=':money_with_wings: Price:', value=f'{price}')
                    embed.add_field(name=':chart_with_upwards_trend: Floor: ', value=f'{fp}')

                    timestamp = parser.parse(addr[i]["event_timestamp"])
                    now = t.time()
                    offset = datetime.datetime.fromtimestamp(now) - datetime.datetime.utcfromtimestamp(now)
                    saletime = timestamp + offset
                    embed.timestamp = saletime
                    embed.set_footer(text='Sent by Argus')
                    embed.set_image(url=img)
                    await ch.send(embed=embed)
                    embed.clear_fields()
                if len(addr) > 0:
                    contract['lastId'] = addr[0]['id']


        with open("data/opensea.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)


    @check_for_sales.before_loop
    async def before_check_for_sales(self):
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
