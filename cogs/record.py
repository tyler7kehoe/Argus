import discord
import os
from api.data_handler import *
from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import Button, View, InputText, Modal



class default(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot=bot

    @commands.command(guild_ids=[int(os.getenv("GUILD_ID"))])
    async def logging(self, ctx):
        button_enter = Button(label='Log Your Address Here!', style=discord.ButtonStyle.green)
        button_grab = Button(label='Get your address!', style=discord.ButtonStyle.blurple, emoji="📄")

        async def button_callback(interaction):
            modal = MyModal()
            await interaction.response.send_modal(modal)

        async def button_grabber(interaction):
            user_id = interaction.user.id
            address = await get_input(user_id)
            await interaction.response.send_message(f'{interaction.user.mention} {address}', ephemeral=True)

        button_enter.callback = button_callback
        button_grab.callback = button_grabber

        view = View(timeout=0)
        view.add_item(button_enter)
        view.add_item(button_grab)
        await ctx.send('Enter your wallet address:', view=view)


class MyModal(Modal):
    def __init__(self) -> None:
        super().__init__("Wallet Form")  # FORM HEADER - feel free to change
        self.add_item(InputText(label="Enter Wallet Address Here:", placeholder="Wallet Address"))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="User Wallet Log", color=discord.Color.brand_red())
        embed.add_field(name="Wallet Address Logged",  value="Thank you", inline=True)
        address = self.children[0].value
        user_id = interaction.user.id

        await set_input(user_id, address)
        await interaction.response.send_message("{} your address has been logged".format(interaction.user.mention), ephemeral=True)


def setup(bot):
    bot.add_cog(default(bot))
