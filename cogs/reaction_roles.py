import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import json

load_dotenv()


class reaction_roles(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="reaction_roles", description="Click reactions for reaction roles")
    async def reactionroles(self, ctx: Context):

        def check(m):
            return m.content and m.channel == ctx.channel
        try:
            await ctx.respond('What roles will be included in the reaction roles embed? '
                              'Make sure to use the @ specifier for each role.')
            rolls = await self.bot.wait_for("message", check=check, timeout=240)
            rolls_list = rolls.content.split()
            for i in range(len(rolls_list)):
                rolls_list[i] = rolls_list[i][3:]
                rolls_list[i] = rolls_list[i][:-1]
                rolls_list[i] = ctx.guild.get_role(int(rolls_list[i]))
                rolls_list[i] = rolls_list[i].name
            await ctx.respond('What emojis would you like to use for the users to select their roles? Please have the emojis'
                              ' separated by a space and correspond to the order you listed the roles')
            proper_length = False
            while not proper_length:
                emojis = await self.bot.wait_for("message", check=check, timeout=240)
                emojis = emojis.content.split()
                if len(emojis) == len(rolls_list):
                    proper_length = True
                else:
                    await ctx.respond('Ensure you enter the correct number of emojis per role')

            emoji_list = emojis
            await ctx.respond('What channel would you like the embed to appear in? (Please input as #channel-name)')
            chID_msg = await self.bot.wait_for("message", check=check, timeout=240)
        except asyncio.TimeoutError:
            await ctx.respond('You took too long to respond to the message (Timeout after 4 minutes.)')
        except ValueError:
            await ctx.respond('There was likely an input error. Please try again')

        chID_stripped = chID_msg.content[2:]
        chID_stripped = chID_stripped[:-1]
        chID = self.bot.get_channel(int(chID_stripped))

        embed = discord.Embed(title="Select Roles!", color=discord.Color.brand_red())

        role_dict = dict(zip(emoji_list, rolls_list))

        for emoji in role_dict.keys():
            embed.add_field(name=f'{emoji} =', value=f'{discord.utils.get(chID.guild.roles, name=role_dict[emoji]).mention}')
        embed.set_footer(text='Please react to the emoji of your desired role')

        reaction_roles_msg = await chID.send(embed=embed)
        for i in emojis:
            await reaction_roles_msg.add_reaction(i)
        await self.log_msg(reaction_roles_msg.id, reaction_roles_msg.channel.id, rolls_list, emoji_list)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        obj = None
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        guild = await self.bot.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        emoji = str(payload.emoji.id) if payload.emoji.is_custom_emoji() else payload.emoji.name
        with open("reaction_roles.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            for item in data:
                if item["message_id"] == message.id:
                    obj = item
            if obj is None:
                return
        num = -1
        emList = obj['emojis']
        for i in range(len(emList)):
            if emList[i] == emoji:
                num = i
        role = discord.utils.get(message.guild.roles, name=obj["roles"][num])
        if member != self.bot.user:
            await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        obj = None
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        emoji = str(payload.emoji.id) if payload.emoji.is_custom_emoji() else payload.emoji.name
        with open("reaction_roles.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            for item in data:
                if item["message_id"] == message.id:
                    obj = item
            if obj is None:
                return
        num = -2
        emList = obj['emojis']
        # Remove reactions not in role list
        if emoji not in emList:
            await message.remove_reaction(emoji, payload.member)
        # Finds location of emoji in list so we know what role to add
        for i in range(len(emList)):
            if emList[i] == emoji:
                num = i
        role = discord.utils.get(message.guild.roles, name=obj["roles"][num])
        if payload.member != self.bot.user:
            await payload.member.add_roles(role)

    async def log_msg(self, message_id, ch_id, roles, emojis):
        with open("reaction_roles.json", "r", encoding="UTF-8") as _:
            data = json.load(_)

            new_set = {
                "message_id": message_id,
                "host_channel": ch_id,
                "roles": roles,
                "emojis": emojis
            }

            if new_set not in data:
                data.append(new_set)

        with open("reaction_roles.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)


def setup(bot):
    bot.add_cog(reaction_roles(bot))
