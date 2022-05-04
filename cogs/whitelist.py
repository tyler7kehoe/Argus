import json

import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, View, InputText, Modal
import pandas as pd


class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="whitelist", description="Call button to log whitelist addresses")
    async def whitelist(self, ctx: Context):
        enter_button = Button(label='Enter here!', style=discord.ButtonStyle.blurple)

        # call input box to screen after button click
        async def button_callback(interaction):
            modal = Popup()
            await interaction.response.send_modal(modal)

        enter_button.callback = button_callback

        view = View(timeout=0)
        view.add_item(enter_button)
        await ctx.respond('Buttons sent!', ephemeral=True)
        await ctx.send('Congratulations on winning whitelist, please enter wallet address here', view=view)

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="get_whitelist", description="Get CSV file of all whitelist addresses")
    async def get_whitelist(self, ctx: Context):
        # df = pd.read_json(r'data/whitelist.json')
        with open("data/whitelist.json", "r") as _:
            data = json.load(_)
            for item in data:
                if item['guild_id'] == ctx.guild.id:
                    whitelist_data = item['whitelist']
        df = pd.DataFrame(whitelist_data, columns=['Addresses'])
        df.to_csv(rf'data/whitelists/{ctx.guild.name}-whitelist.csv', index=None)
        await ctx.respond('Whitelist sent!')
        await ctx.send(file=discord.File(rf'data/whitelists/{ctx.guild.name}-whitelist.csv'))

# creation of input text pop-up
class Popup(Modal):
    def __init__(self) -> None:
        super().__init__("Enter Wallet Here")  # FORM HEADER - feel free to change
        self.add_item(InputText(label="Wallet Address:", placeholder="Wallet Address"))

    async def callback(self, interaction: discord.Interaction):
        # get wallet address from input box
        address = self.children[0].value

        await set_input(interaction.guild.id, address)
        await interaction.response.send_message("{} your address has been logged".format(interaction.user.mention), ephemeral=True)


async def set_input(guild_id, wallet):
    with open("data/whitelist.json", "r") as _:
        data = json.load(_)

        found = False
        new_set = {
            "guild_id": guild_id,
            "whitelist": [wallet]
        }

        for i in data:
            if i['guild_id'] == guild_id:
                found = True
                i['whitelist'].append(wallet)

        if not found:
            data.append(new_set)

    with open("data/whitelist.json", "w") as _:
        json.dump(obj=data, fp=_, indent=4)



def setup(bot):
    bot.add_cog(Whitelist(bot))