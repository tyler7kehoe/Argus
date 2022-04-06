from datetime import datetime
import discord

from enum import Enum

def embed_builder(title,user,description,color,footer=None):
    embed = discord.Embed()
    if user.avatar is not None:
        embed.set_author(name=title,icon_url=user.avatar.url)
    else:
        embed.set_author(name=title)
    embed.color = color.value
    embed.description = description
    if footer is not None:
        embed.set_footer(text=footer)
    embed.timestamp = datetime.now()
    
    return embed

class embed_color(Enum):
    SUCCESS = 0x32a852
    FAILURE = 0xde4040
    NEUTRAL = 0x9966cc