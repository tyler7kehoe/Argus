import datetime
import json
import os
import discord
from discord.ext import commands, tasks
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import requests

load_dotenv()
 
# TODO test with larger time frames
# maybe add a time field in the JSON (rather than last accessed) to ensure no time is missed

class Opensea_task(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.printer.start()
        

    def cog_unload(self):
        self.printer.cancel()

    headers = {
                "Accept": "application/json",
                "X-API-KEY": os.getenv("OPENSEA_KEY")
            }


    @tasks.loop(seconds=15.0)
    async def printer(self):
        print("checking for new opensea sales...")
        # time = prevtime
        # time_delta = datetime.datetime.utcnow() - prevtime
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)

        for task in data:
            print("prev: " + str(self.prevtime))
            print("now: " + str(datetime.datetime.utcnow()))
            time_delta = datetime.datetime.utcnow() - self.prevtime
            print("delta: " + str(time_delta))
            print()

            chid = task['channel_id']
            ch = self.bot.get_channel(chid)
            contract_address = task['contract_address']

            params = {
            "only_opensea": 'true',            
            'asset_contract_address': contract_address,
            "event_type": 'successful',
            # "occurred_after": datetime.datetime.utcnow() - datetime.timedelta(seconds=5),
            # "occurred_after": datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
            "occurred_after": datetime.datetime.utcnow() - time_delta,
            }
            # print(datetime.datetime.utcnow())
            contract = requests.get("https://api.opensea.io/api/v1/events?event_type=successful", params=params, headers=self.headers)
            contract = contract.json()
            contract = contract['asset_events']
            print(contract)

            for i in range(len(contract)):
                title = contract[i]['asset']['name']
                description = contract[i]['asset']['asset_contract']["name"]
                img = contract[i]['asset']['image_url']
                from_acc = contract[i]['transaction']['from_account']['address']
                to_acc = contract[i]['winner_account']['address']

                embed = discord.Embed(title=f"{title}", color=discord.Color.blue(),
                                description=f'{description}')
                embed.add_field(name='Seller:', value=f'[{from_acc[:-35]}](https://etherscan.io/address/{from_acc})')
                embed.add_field(name='Buyer:', value=f'[{to_acc[:-35]}](https://etherscan.io/address/{to_acc})')     # trouble reaching buyer location with indexing.
                embed.timestamp = datetime.datetime.now()

                embed.set_image(url=img)
                await ch.send(embed=embed)
        print()
        print()
        self.prevtime = datetime.datetime.utcnow()

    @printer.before_loop
    async def before_printer(self):
        self.prevtime = datetime.datetime.utcnow()
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Opensea_task(bot))