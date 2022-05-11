import discord
from discord.ext import commands
from discord.ui import Button, View, InputText, Modal
from api.data_handler import *

class default(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot=bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="logging", description="Log wallets for giveaways")
    async def logging(self, ctx):
        button_enter = Button(label='Log Your Address Here!', style=discord.ButtonStyle.green)
        button_grab = Button(label='Get your address!', style=discord.ButtonStyle.blurple, emoji="📄")

        async def button_callback(interaction):
            modal = MyModal()
            await interaction.response.send_modal(modal)

        async def button_grabber(interaction):
            user_id = interaction.user.id
            guild_id = interaction.guild.id
            address = await get_input(guild_id, user_id)
            await interaction.response.send_message(f'{interaction.user.mention} {address}', ephemeral=True)

        button_enter.callback = button_callback
        button_grab.callback = button_grabber

        view = View(timeout=0)
        view.add_item(button_enter)
        view.add_item(button_grab)
        await ctx.send('Enter your wallet address:', view=view)
        await ctx.respond('Buttons sent!', ephemeral=True)


class MyModal(Modal):
    def __init__(self) -> None:
        super().__init__("Wallet Form")  # FORM HEADER - feel free to change
        self.add_item(InputText(label="Enter Wallet Address Here:", placeholder="Wallet Address"))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="User Wallet Log", color=discord.Color.brand_red())
        embed.add_field(name="Wallet Address Logged",  value="Thank you", inline=True)
        address = self.children[0].value
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        await set_input(guild_id, user_id, address)
        await interaction.response.send_message("{} your address has been logged".format(interaction.user.mention), ephemeral=True)


def setup(bot):
    bot.add_cog(default(bot))
