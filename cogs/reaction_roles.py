import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import json

load_dotenv()

global channel_id, emoji_list, rolls_list, role_dict


class reaction_roles(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="reaction_roles", description="Click reactions for reaction roles")
    async def reactionroles(self, ctx: Context):
        global channel_id, emoji_list, rolls_list, role_dict

        def check(m):
            return m.content and m.channel == ctx.channel
        await ctx.respond('What roles will be included in the reaction roles embed?')
        rolls = await self.bot.wait_for("message", check=check)
        rolls_list = rolls.content.split()

        await ctx.respond('What emojis would you like to use for the users to select their roles? Please have the emojis'
                          ' separated by a space and correspond to the order you listed the roles')
        proper_length = False
        while not proper_length:
            emojis = await self.bot.wait_for("message", check=check)
            emojis = emojis.content.split()
            if len(emojis) == len(rolls_list):
                proper_length = True
            else:
                await ctx.respond('Ensure you enter the correct number of emojis per role')

        emoji_list = emojis
        await ctx.respond('What channel would you like the embed to appear in? (Please input as #channel-name)')
        chID_msg = await self.bot.wait_for("message", check=check)
        chID_stripped = chID_msg.content[2:]
        chID_stripped = chID_stripped[:-1]
        chID = self.bot.get_channel(int(chID_stripped))
        channel_id = chID

        embed = discord.Embed(title="Select Roles!", color=discord.Color.brand_red())

        role_dict = dict(zip(emoji_list, rolls_list))

        for emoji in role_dict.keys():
            embed.add_field(name=f'{emoji} =', value=f'{discord.utils.get(chID.guild.roles, name=role_dict[emoji]).mention}')

        reaction_roles_msg = await chID.send(embed=embed)
        for i in emojis:
            await reaction_roles_msg.add_reaction(i)
        await self.log_msg(reaction_roles_msg.id, reaction_roles_msg.channel.id, rolls_list, emoji_list)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global channel_id, emoji_list, rolls_list, role_dict

        if reaction.message.channel.id != channel_id.id:
            return
        role_name = role_dict[reaction.emoji]
        role = discord.utils.get(reaction.message.guild.roles, name=role_name)
        if user != self.bot.user:
            await user.add_roles(role)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        global channel_id
        if reaction.message.channel.id != channel_id.id:
            return
        role_name = role_dict[reaction.emoji]
        role = discord.utils.get(reaction.message.guild.roles, name=role_name)
        await user.remove_roles(role)

    # TODO: Create JSON, input message/channel id's as well as corresponding roles and emojis.

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        with open("reaction_roles.json", "r") as _:
            data = json.load(_)
            for item in data:
                if item["message_id"] == message.id:
                    obj = item
        # if await message.channel.fetch_message(payload.message_id) != obj["message_id"]:
        #     return
        role = "role1"
        if payload.member != self.bot.user:
            await payload.member.add_roles(role)

    async def log_msg(self, message_id, ch_id, roles, emojis):
        with open("reaction_roles.json", "r") as _:
            data = json.load(_)

            new_set = {
                "message_id": message_id,
                "host_channel": ch_id,
                "roles": roles,
                "emojis": emojis
            }

            if new_set not in data:
                data.append(new_set)

        with open("reaction_roles.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)


def setup(bot):
    bot.add_cog(reaction_roles(bot))
