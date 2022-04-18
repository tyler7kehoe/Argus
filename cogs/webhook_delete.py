import discord
from discord.ext import commands
from api import embed_builder


class WebhookDelete(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener('on_message')
    async def del_webhook(self, message):
        if message.webhook_id is None:
            return
        elif message.type is discord.MessageType.application_command or message.author == self.bot.user:
            return
        else:
            wh = await self.bot.fetch_webhook(message.webhook_id)
            audit_logs = await wh.guild.audit_logs(limit=100).flatten()
            await wh.delete(reason='Illegal webhook use')
            await message.delete()
            for entry in audit_logs:
                if wh is not None:
                    if entry.action is not None and entry.action is discord.AuditLogAction.webhook_create:
                        if entry.target.id == wh.id:
                            if entry.user is not None and entry.user.id is not self.bot.user:
                                member = await wh.guild.fetch_member(entry.user.id)
                                if member is not None:
                                    mem_list = member.roles
                                    mem_list.pop(0)
                                    for role in mem_list:
                                        await member.remove_roles(role, reason=f'Created webhook {entry.id}')
                                    for channel in member.guild.channels:
                                        await channel.set_permissions(member, send_messages=False, view_channel=False,
                                                                      view_guild_insights=False)
                                    em = embed_builder.embed_builder('Webhook Detected!',
                                                                f'{member.name} created and sent a webhook!',
                                                                embed_builder.embed_color.FAILURE,
                                                                footer='Check audit logs for more info')





def setup(bot):
    bot.add_cog(WebhookDelete(bot))
