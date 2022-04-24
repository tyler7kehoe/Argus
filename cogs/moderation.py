import json
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv
from api import embed_builder

load_dotenv()

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="add_to_blacklist", description="Separate words by comma, no spaces")
    async def add_to_blacklist(self, ctx: Context, blacklist, channel_to_log):
        blacklist = str(blacklist).split(',')
        chID = channel_to_log[2:]
        chID = chID[:-1]
        await self.log_term(ctx.guild.id, blacklist, chID)
        await ctx.respond(f'Terms {blacklist} added to blacklist.')

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="remove_from_blacklist", description="Separate words by comma, no spaces")
    async def remove_from_blacklist(self, ctx: Context, terms):
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
                        ctx.respond('The words you entered were not found in the blacklist, removal failed.')
                    elif (init_len-len(terms)) != len(curr_blacklist):
                        ctx.respond('Not all terms were removed! Make sure you enter them correctly.')
                    else:
                        await ctx.respond(f'{terms} removed from blacklist.')
        with open("data/blacklist.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="get_blacklist", description="Returns list of blacklisted terms that are not allowed"
                                                              "to be in server members names")
    async def retrieve_blacklist(self, ctx: Context):
        blacklist = list(await self.get_blacklist(ctx.guild.id))
        await ctx.respond(blacklist)

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

    async def log_term(self, guild_id, blacklist, channel_to_log):
        with open("data/blacklist.json", "r", encoding="UTF-8") as _:
            data = json.load(_)
            found = False
            new_set = {
                "guild_id": guild_id,
                "blacklist": blacklist,
                "channel_id": channel_to_log
            }

            for set in data:
                if set["guild_id"] == guild_id:
                    for item in blacklist:
                        set["blacklist"].append(item)
                    found = True

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


def setup(bot):
    bot.add_cog(Moderation(bot))
