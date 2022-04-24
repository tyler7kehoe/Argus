import json
import discord
import os
from discord.ext import commands, tasks
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import requests


load_dotenv()


class openseas_sales(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="opensea",
                            description="Automatically post opensea sales in an embed")
    async def opensea(self, ctx: Context, channel, contract_address):

        ch = self.bot.get_channel(int(channel[2:-1]))

        headers = {
            "Accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_KEY")
        }

        params = {
            'asset_contract_address': contract_address
        }

        contract = requests.get("https://api.opensea.io/api/v1/assets", params=params, headers=headers)
        contract = contract.json()
        # log the new contract per guild specific
        self.log_contract_tracker(ctx.guild, ch, contract_address)

        await self.send_embed(ctx, ch, contract)

    async def send_embed(self, context, ch, contract):
        embed = discord.Embed(title=f"{contract['assets'][0]['name']}", color=discord.Color.blue(),
                              description=f'{contract["assets"][0]["asset_contract"]["name"]}')
        # embed.add_field(name='Seller:', value=f'[{contract["assets"][0]["from_account"]["address"][:-35]}](https://etherscan.io/address/{contract["assets"][0]["from_account"]["address"]})')
        # embed.add_field(name='Buyer:', value=f'[{contract["assets"][0]["to_account"][:-35]}](https://etherscan.io/address/{contract["assets"][0]["to_account"]})')     # trouble reaching buyer location with indexing.

        try:
            embed.set_image(url=contract['assets'][0]['large_image_url'])
        except KeyError:
            embed.set_image(url=contract['assets'][0]['image_url'])
        await ch.send(embed=embed)
        await context.respond('Contract sent to designated text-channel')

    def log_contract_tracker(self, guild_id, channel_id, contract_address):
        with open("data/blacklist.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            contract_addresses = list()
            new_set = {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'contract_addresses': contract_addresses.append(contract_address)
            }

            for set in data:
                if set["guild_id"] == guild_id:
                    set["contract_addresses"].append(contract_address)

            if new_set not in data:
                data.append(new_set)

        with open("data/blacklist.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)

    # @tasks.loop(minutes=1):
    # async def check_for_transactions(self, contract):
    #     pass


def setup(bot):
    bot.add_cog(openseas_sales(bot))
