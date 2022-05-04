import discord
import os
from discord.ext import commands
from asyncio import sleep
from dotenv import load_dotenv

from cogs.giveaway import giveaway


load_dotenv()
intents = discord.Intents.default()
intents.members = True
prefix = commands.when_mentioned_or('-')
bot = commands.Bot(command_prefix=prefix, intents=intents)


def load_extensions(directory):
    for file in os.listdir(directory):
        if file.endswith(".py"):
            dir = directory.replace(".py", "").replace("./", "")
            try:
                bot.load_extension(f"{dir}.{file[:-3]}")
                print(f"[Bot] Loaded extension {file[:-3]} in {dir}!")
            except discord.ExtensionFailed as error:
                print(f"[Bot] Couldn't load extension {file[:-3]} in {dir}!\n      [Error] {error}")
        elif os.path.isdir(f"./cogs/{file}") is True:
            load_extensions(f"./cogs/{file}")


load_extensions("./cogs")


@bot.event
async def on_ready():
    print(f"[Bot] I have started up and logged in {bot.user.name}#{bot.user.discriminator}!")
    g = giveaway(bot)
    await g.check_for_active_giveaways(bot)


@bot.event
async def on_member_join(member):
    await sleep(10*60)
    for channel in member.guild.channels:
        if channel.name.startswith('member'):
            await channel.edit(name=f'Members | {member.guild.member_count}')
            break


bot.run(os.getenv("TOKEN"))
