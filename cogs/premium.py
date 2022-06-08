import json
import openpyxl
import pandas as pd
from datetime import date

import discord
from discord.ext import commands
from discord.ext.commands.context import Context

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = commands.Bot = bot

    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name='premium', description='Activate Argus premium in this server')
    async def premium(self, ctx: Context, code):
        # first, open the csv file and search to see if the code is in the file.
        df = pd.read_excel('data/premium_codes.xlsx')
        codes = df['codes'].tolist()
        counter = 0
        for item in codes:
            # if code is in the file, add the guild and user to the json file. S2ZSEtfPnX
            if item == code:
                guild = ctx.guild.id
                premium_owner = ctx.author.name + '#' + ctx.author.discriminator     # (Argus premium)
                with open("data/active_premium.json", "r") as _:
                    data = json.load(_)
                    new_set = {
                        'user_id': premium_owner,
                        'guild_id': guild,
                        'date': str(date.today())
                    }
                    data.append(new_set)
                    print(f'[Bot] Premium unlocked by {premium_owner} with code {item} for guild "{ctx.guild.name}"')
                with open("data/active_premium.json", "w") as _:
                    json.dump(obj=data, fp=_, indent=4)

                # remove code from the csv file
                codes.remove(item)
                # create dict for df
                code_dict = {'codes': codes}
                xlsx = pd.DataFrame(code_dict)
                xlsx.to_excel('data/premium_codes.xlsx', sheet_name="Sheet 1", index=False)
                await ctx.respond(f'```json\n"This server has been added to premium under name {premium_owner}!\n\n'
                                  f'Please contact the Argus team with any issues!\n\nThank you!"\n```')

                return
            counter += 1


def check_if_guild_has_premium(ctx: Context):
    with open("data/active_premium.json", "r") as _:
        data = json.load(_)
        for item in data:
            guild = ctx.guild.id
            if item['guild_id'] == guild:
                return True
        return False


async def error_msg(error, ctx):
    if isinstance(error, discord.CheckFailure):
        await ctx.respond('```diff\n- You are required to have the premium version of Argus to use this command!\n\n'
                          '+ Please contact the Argus developers if looking for premium!\n```')
    else:
        raise error

def setup(bot):
    bot.add_cog(Premium(bot))




