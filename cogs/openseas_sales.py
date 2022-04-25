import datetime
import json
import discord
import os
from discord.ext import commands, tasks
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import requests
from multiprocessing import Pool

load_dotenv()
global task_schedule

class Openseas_Sales(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.opensea_contracts = TaskHandler(bot)

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="opensea",
                            description="Automatically post opensea sales in an embed")
    async def opensea(self, ctx: Context, channel, contract_address):
        global task_schedule
        ch = self.bot.get_channel(int(channel[2:-1]))
        guild_id = ctx.guild.id
        headers = {
            "Accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_KEY")
        }

        params = {
            'asset_contract_address': contract_address
        }

        contract = requests.get("https://api.opensea.io/api/v1/events?event_type=successful", params=params, headers=headers)
        contract = contract.json()
        contract = contract['asset_events']
        # log the new contract per guild specific
        self.log_contract_tracker(guild_id, ch.id, contract_address, last_transaction=contract[0]['transaction']['transaction_hash'])

        title = contract[0]['asset']['name']
        description = contract[0]['asset']['asset_contract']["name"]
        img = contract[0]['asset']['image_url']
        from_acc = contract[0]['transaction']['from_account']['address']
        to_acc = contract[0]['winner_account']['address']

        self.opensea_contracts.start_task(guild_id)

        await self.send_embed(ch, title, description, img, from_acc, to_acc)
        await ctx.respond('Most recent transaction sent to designated text-channel\n'
                          'Transactions from this contract will now be tracked.')


    async def send_embed(self, ch, title, description, img, from_acc, to_acc):
        embed = discord.Embed(title=f"{title}", color=discord.Color.blue(),
                              description=f'{description}')
        embed.add_field(name='Seller:', value=f'[{from_acc[:-35]}](https://etherscan.io/address/{from_acc})')
        embed.add_field(name='Buyer:', value=f'[{to_acc[:-35]}](https://etherscan.io/address/{to_acc})')     # trouble reaching buyer location with indexing.
        embed.timestamp = datetime.datetime.now()

        embed.set_image(url=img)
        await ch.send(embed=embed)

    def log_contract_tracker(self, guild_id, channel_id, contract_address, last_transaction=None):
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            new_set = {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'contract_address': contract_address,
                'last_transaction': last_transaction
            }

            for item in data:
                if item['guild_id'] == guild_id:
                    item['channel_id'] = channel_id
                    item['contract_address'] = contract_address
                    item['last_transaction'] = last_transaction

            if new_set not in data:
                data.append(new_set)

        with open("data/opensea.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)

    def get_contract_tracker(self, guild_id):
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            for item in data:
                if item['guild_id'] == guild_id:
                    return item['contract_address'], item['channel_id'], item['last_transaction']
    # TODO: this does not work!!!! (also could do re_init in TaskHandler)
    @tasks.loop(seconds=10)
    async def ensure_tasks(self):
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            to_init = list()
            for item in data:
                to_init.append(item)

            with Pool(len(to_init)) as p:
                p.map(self.start_task, (item['guild_id'] for item in to_init))



def setup(bot):
    bot.add_cog(Openseas_Sales(bot))


class TaskHandler:
    def __init__(self, bot):
        self._tasks = []
        self.bot = bot

    async def check_for_new_transaction(self, guild_id):
        # This is the function that will be 'looping'
        new_txns = list()

        openseas_obj = Openseas_Sales(self.bot)
        contract_address, channel_id, last_transaction = openseas_obj.get_contract_tracker(guild_id)
        ch = self.bot.get_channel(channel_id)

        headers = {
            "Accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_KEY")
        }

        params = {
            'asset_contract_address': contract_address
        }

        contract = requests.get("https://api.opensea.io/api/v1/events?event_type=successful", params=params,
                                headers=headers)
        txns = contract.json()
        txns = txns['asset_events']

        for item in txns:
            new_txns.append(item)
            if item['transaction']['transaction_hash'] == last_transaction:
                new_txns.pop()
                if len(new_txns) != 0:
                    for txn in new_txns:
                        title = txn['asset']['name']
                        description = txn['asset']['asset_contract']["name"]
                        img = txn['asset']['image_url']
                        from_acc = txn['transaction']['from_account']['address']
                        to_acc = txn['winner_account']['address']                  # todo: find difference between seller and buyer addr in json
                        await openseas_obj.send_embed(ch, title, description, img, from_acc, to_acc)
                new_txns.clear()
                break

    def task_launcher(self, guild_id):
        """Creates new instances of `tasks.Loop`"""
        # Creating the task
        new_task = tasks.loop(minutes=1)(self.check_for_new_transaction)
        # Starting the task
        new_task.start(guild_id)
        self._tasks.append(new_task)

    def start_task(self, guild_id):
        """Command that launches a new task with the arguments given"""
        self.task_launcher(guild_id)
        print(f'Task {guild_id} started!')

    def reinit(self):
        with open("data/opensea.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            to_init = list()
            for item in data:
                to_init.append(item)
            # await asyncio.gather(*(self.task_launcher(item['guild_id']) for item in data))
            # TODO: figure out how to get all of the tasks to startup simultaneously
            # for item in data:
            #     self.task_launcher(item['guild_id'])
            with Pool(len(to_init)) as p:
                p.map(self.start_task, (item['guild_id'] for item in data))

    def get_tasks(self):
        return self._tasks


