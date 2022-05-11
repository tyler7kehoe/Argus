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
        enter_button = Button(label='Enter here!', style=discord.ButtonStyle.blurple, custom_id='b1')
        button_grab = Button(label='Get your address!', style=discord.ButtonStyle.green, emoji="📄")



        enter_button.callback = self.button_callback
        button_grab.callback = self.button_grabber

        view = View(timeout=0)
        view.add_item(enter_button)
        view.add_item(button_grab)
        await ctx.respond('Button sent!', ephemeral=True)
        await ctx.send('Congratulations on winning whitelist, please enter wallet address here', view=view)

    # call input box to screen after button click
    async def button_callback(self, interaction):
        modal = Popup()
        await interaction.response.send_modal(modal)

    async def button_grabber(self, interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        address = await get_input(user_id, guild_id)
        await interaction.response.send_message(f'{interaction.user.mention} {address}', ephemeral=True)

    # TODO: find way to cache button and use
    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.custom_id == 'b1':
            modal = Popup()
            await interaction.response.send_modal(modal)


    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="get_whitelist", description="Get CSV file of all whitelist addresses")
    async def get_whitelist(self, ctx: Context):
        # Get list of wallet addresses from specific guild
        with open("data/whitelist.json", "r") as _:
            data = json.load(_)
            whitelist_data = list()
            for item in data:
                if item['guild_id'] == ctx.guild.id:
                    for i in item['whitelist']:
                        whitelist_data.append(i['wallet_address'])
        # convert from json data into a csv
        df = pd.DataFrame(whitelist_data, columns=['Addresses'])
        df.to_csv(rf'data/whitelists/{ctx.guild.name}-whitelist.csv', index=None)
        # send to user
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

        await set_input(interaction.guild.id, interaction.user.id, address)
        await interaction.response.send_message("{} your address has been logged".format(interaction.user.mention), ephemeral=True)


async def set_input(guild_id, user_id, wallet):
    with open("data/whitelist.json", "r") as _:
        data = json.load(_)

        found = False
        found_user = False
        new_set = {
            "guild_id": guild_id,
            "whitelist": [{"user_id": user_id, "wallet_address": wallet}]
        }

        for i in data:
            if i['guild_id'] == guild_id:
                found = True
                for j in i['whitelist']:
                    if j['user_id'] == user_id:
                        j['wallet_address'] = wallet
                        found_user = True
                if not found_user:
                    i['whitelist'].append({"user_id": user_id, "wallet_address": wallet})

        if not found:
            data.append(new_set)

    with open("data/whitelist.json", "w") as _:
        json.dump(obj=data, fp=_, indent=4)

async def get_input(user_id, guild_id):
    with open("data/whitelist.json", "r") as _:
        data = json.load(_)

        for i in data:
            if i['guild_id'] == guild_id:
                for j in i['whitelist']:
                    if j['user_id'] == user_id:
                        return j['wallet_address']



def setup(bot):
    bot.add_cog(Whitelist(bot))
