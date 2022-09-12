import os
import traceback

import asyncio
import discord
from discord.ext import commands



class reload(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot=bot
    @commands.command(
            name='reloadcocks420', description="Reload all/one of the bots cogs!"
        )
    @commands.has_permissions(ban_members=True)
    async def reloadallcogs(self, ctx, cog=None):
        if not cog:
                # No cog, means we reload all cogs
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                    )
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`",
                                value='\uFEFF',
                                inline=False
                                )
                        except Exception as e:
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`",
                                value=e,
                                inline=False
                                )
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
                # reload the specific cog
            async with ctx.typing():
                embed = discord.Embed(
                    title=f"Reloading '{cog}' cog!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                    )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                        # if the file does not exist
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`",
                                value='\uFEFF',
                                inline=False
                            )
                        except Exception:
                            desired_trace = traceback.format_exc()
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`",
                                value=desired_trace,
                                inline=False
                            )        
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(reload(bot))
