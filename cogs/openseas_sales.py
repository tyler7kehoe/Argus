import json
import discord
import os
from discord.ext import commands
from discord.ext.commands.context import Context
from opensea import OpenseaAPI
from dotenv import load_dotenv

load_dotenv()


class openseas_sales(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="opensea",
                            description="Automatically post opensea sales in an embed")
    async def opensea(self, ctx: Context, channel, contract_address, token_id):

        ch = self.bot.get_channel(int(channel[2:-1]))

        api = OpenseaAPI(apikey=os.getenv("OPENSEA_KEY"))

        result = api.asset(contract_address, token_id)
        with open("opensea.json", "r") as _:
            data = json.load(_)
            data.append(result)
        with open("opensea.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)
        with open("opensea.json", "r") as _:
            data = json.load(_)
            embed = discord.Embed(title=f"{result['asset_contract']['name']}", color=discord.Color.blue(), description=f'{result["name"]}')
            embed.add_field(name='Seller:', value=f'[{result["asset_contract"]["address"][:-35]}](https://etherscan.io/address/{result["asset_contract"]["payout_address"]})')
            embed.add_field(name='Buyer:', value=f'[{result["asset_contract"]["address"][:-35]}](https://etherscan.io/address/{result["asset_contract"]["address"]})')                              # make sure buy/sell is in the right order

            try:
                embed.set_image(url=result['large_image_url'])
            except KeyError:
                embed.set_image(url=result['image_url'])

        await ch.send(embed=embed)
        await ctx.respond('Contract sent to designated text-channel')


def setup(bot):
    bot.add_cog(openseas_sales(bot))
