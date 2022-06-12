import json
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands import check
from dotenv import load_dotenv
from api import embed_builder
from cogs.premium import *

load_dotenv()


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="enable_moderation", description="Enable name checking for this server")
    async def enable_moderation(self, ctx: Context, channel_to_log):
        # first check if guild has enabled moderation
        enabled = self.check_if_moderation_enabled(ctx)
        if enabled:
            await ctx.respond('Moderation has already been enabled!\n\nIf you would like to change '
                              'the channel to log bans, please retrieve the current blacklist, then disable and'
                              ' re-enable moderation!', ephemeral=True)
            return
        guild_id = ctx.guild.id
        chID = channel_to_log[2:]
        ch_id = chID[:-1]
        await self.log_term(guild_id, ['bot', 'verification', 'giveaway', 'captcha'], ch_id)
        await ctx.respond('This server has been enabled for moderation with default words bot, verification, giveaway, '
                          'and captcha.\n\nArgus Premium is required to add and delete words!', ephemeral=True)

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="disable_moderation", description="Disable name checking for this server")
    async def disable_moderation(self, ctx: Context):
        guild_id = ctx.guild.id
        found = False
        with open("data/blacklist.json", "r") as _:
            data = json.load(_)
            for item in data:
                if item['guild_id'] == guild_id:
                    data.remove(item)
                    found = True
                    await ctx.respond('This server has been removed from our moderation tool!', ephemeral=True)
        with open("data/blacklist.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)
        if not found:
            await ctx.respond('Moderation must be enabled before being disabled!', ephemeral=True)

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="add_to_blacklist", description="Separate words by comma, no spaces")
    @check(check_if_guild_has_premium)
    async def add_to_blacklist(self, ctx: Context, blacklist):
        # first check if guild has enabled moderation
        enabled = self.check_if_moderation_enabled(ctx)
        if not enabled:
            await ctx.respond('Moderation must be enabled first! Use /enable_moderation', ephemeral=True)
            return
        blacklist = str(blacklist).split(',')
        new_list = list()
        # strip surrounding whitespace from words and place them in a new list
        for item in blacklist:
            new_list.append(item.strip())
        await self.log_term(ctx.guild.id, new_list)
        await ctx.respond(f'Terms {new_list} added to blacklist.', ephemeral=True)

    @add_to_blacklist.error
    async def add_to_blacklist_error(self, ctx: Context, error):
        await error_msg(error, ctx)

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="remove_from_blacklist", description="Separate words by comma, no spaces")
    @check(check_if_guild_has_premium)
    async def remove_from_blacklist(self, ctx: Context, terms):
        # first check if guild has enabled moderation
        enabled = self.check_if_moderation_enabled(ctx)
        if not enabled:
            await ctx.respond('Moderation must be enabled first! Use /enable_moderation', ephemeral=True)
            return
        terms = str(terms).split(',')
        with open("data/blacklist.json", "r") as _:
            data = json.load(_)
            for item in data:
                if item["guild_id"] == ctx.guild.id:
                    curr_blacklist = list(item["blacklist"])
                    init_len = len(curr_blacklist)
                    i = 0
                    loopcount = len(curr_blacklist)
                    while i < loopcount:
                        for word in terms:
                            if curr_blacklist[i] == word:
                                curr_blacklist.pop(i)
                                loopcount -= 1
                        i += 1
                    item["blacklist"] = curr_blacklist
                    if len(curr_blacklist) == init_len:
                        ctx.respond('The words you entered were not found in the blacklist, removal failed.',
                                    ephemeral=True)
                    elif (init_len - len(terms)) != len(curr_blacklist):
                        ctx.respond('Not all terms were removed! Make sure you enter them correctly.', ephemeral=True)
                    else:
                        await ctx.respond(f'{terms} removed from blacklist.', ephemeral=True)
        with open("data/blacklist.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)

    @remove_from_blacklist.error
    async def remove_from_blacklist_error(self, ctx: Context, error):
        await error_msg(error, ctx)

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="get_blacklist", description="Returns list of blacklisted terms that are not allowed"
                                                              "to be in server members names")
    async def retrieve_blacklist(self, ctx: Context):
        blacklist = list(await self.get_blacklist(ctx.guild.id))
        await ctx.respond(blacklist, ephemeral=True)

    @commands.Cog.listener("on_member_update")
    async def nick_change(self, before, after):
        if before.bot is True:
            return
        elif before.nick != after.nick and after.nick is not None:
            await self.check_for_invalid_terms(after)

    @commands.Cog.listener("on_member_join")
    async def invalid_name(self, member):
        if member.bot is True:
            return
        elif member.display_name is not None:
            await self.check_for_invalid_terms(member)

    async def check_for_invalid_terms(self, member):
        blacklist = list(await self.get_blacklist(member.guild.id))
        for term in blacklist:
            split_name = member.display_name.split()
            for i in range(len(split_name)):
                if term in split_name[i].casefold() or term is member.display_name:
                    await self.send_log(member, term)
                    await member.guild.ban(member, reason=f'Changed nickname to contain {term}')

    async def log_term(self, guild_id, blacklist, channel_to_log=None):
        with open("data/blacklist.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            found = False
            append_new = True  # used for when we are enabling a new server, otherwise changed to
            # false when just adding new words to blacklist.

            if channel_to_log is not None:
                new_set = {
                    "guild_id": guild_id,
                    "blacklist": blacklist,
                    "channel_id": channel_to_log
                }
            else:
                new_set = None
                append_new = False

            for set in data:
                if set["guild_id"] == guild_id:
                    for item in blacklist:
                        set["blacklist"].append(item)
                    found = True

            if append_new is True:
                if new_set not in data and not found:
                    data.append(new_set)

        with open("data/blacklist.json", "w", encoding="UTF-8") as _:
            json.dump(obj=data, fp=_, indent=4)

    async def get_blacklist(self, guild_id):
        with open("data/blacklist.json", "r") as _:
            data = json.load(_)

            for set in data:
                if set['guild_id'] == guild_id:
                    return set['blacklist']
            else:
                return ["Moderation has not been enabled in this server."]

    async def get_chid(self, guild_id):
        with open("data/blacklist.json", "r") as _:
            data = json.load(_)

            for set in data:
                if set['guild_id'] == guild_id:
                    return set['channel_id']

    async def send_log(self, member, term):
        em = embed_builder.embed_builder(f'User [{member.display_name}] was banned!', member,
                                         f'Their name contained {term}',
                                         embed_builder.embed_color.FAILURE,
                                         footer='Check audit logs for more info')
        chID = await self.get_chid(member.guild.id)
        chID = self.bot.get_channel(int(chID))
        await chID.send(embed=em)


    def check_if_moderation_enabled(self, ctx: Context):
        guild_id = ctx.guild.id

        with open("data/blacklist.json", "r") as _:
            data = json.load(_)

            for item in data:
                if item['guild_id'] == guild_id:
                    return True

            return False

def setup(bot):
    bot.add_cog(Moderation(bot))
