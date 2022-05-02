import discord
import time
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv
import os

load_dotenv()


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="setup", description="Setup server with default channels and roles.",
                            guild_ids=[int(os.getenv("GUILD_ID"))])
    async def setup(self, ctx: Context):
        guild = ctx.guild
        
        # Create "Core" role with permissions
        core = await guild.create_role(name="Core", permissions=discord.Permissions.all(), color=0xFF0000)
        
        # Create "Lead Mods" role with permissions
        perms = discord.Permissions(141972467270)
        lead_mods = await guild.create_role(name="Lead Mods", permissions=perms, color=0xFFFF00)

        # # Create "Mods" role with permissions 
        perms = discord.Permissions(141838249538)
        mods = await guild.create_role(name="Mods", permissions=perms, color=0x00FF00)

        # Create "Verified" role with permissions
        perms = discord.Permissions(141838077504)
        verified = await guild.create_role(name="Verified", permissions=perms, color=0x00FFFF)

        await ctx.respond("Roles created")

        # Permission overwrites for channel accesss
        general_overwrite = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            lead_mods: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            mods: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            verified: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        official_things_overwrite = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            core: discord.PermissionOverwrite(send_messages=True),
            lead_mods: discord.PermissionOverwrite(send_messages=False),
            mods: discord.PermissionOverwrite(send_messages=False),
            verified: discord.PermissionOverwrite(send_messages=False)
        }
        team_overwrite = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            lead_mods: discord.PermissionOverwrite(view_channel=False),
            mods: discord.PermissionOverwrite(view_channel=False),
            verified: discord.PermissionOverwrite(view_channel=False)
        }
        start_overwrite = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            lead_mods: discord.PermissionOverwrite(view_channel=False),
            mods: discord.PermissionOverwrite(view_channel=False),
            verified: discord.PermissionOverwrite(view_channel=False)
        }
        mods_overwrite = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            lead_mods: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            mods: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            verified: discord.PermissionOverwrite(view_channel=False)
        }



        # Create Categories
        team = await guild.create_category("TEAM", overwrites=team_overwrite)
        start_here = await guild.create_category("START HERE", overwrites=start_overwrite)
        official_things = await guild.create_category("OFFICIAL THINGS", overwrites=official_things_overwrite)        
        general = await guild.create_category("GENERAL", overwrites=general_overwrite)
        voice_chats = await guild.create_category("VOICE CHATS", overwrites=general_overwrite)
        languages = await guild.create_category("LANGUAGES", overwrites=general_overwrite)
        support = await guild.create_category("SUPPORT TICKETS", overwrites=general_overwrite)
        
        # Create Channels
        core_chan = await guild.create_text_channel("core", category=team)
        bot_commands = await guild.create_text_channel("bot-commands", category=team)
        mod_chat = await guild.create_text_channel("mod-chat", category=team, overwrites=mods_overwrite)

        verification = await guild.create_text_channel("verification", category=start_here)

        rules_chan = await guild.create_text_channel("rules", category=official_things)
        announcements = await guild.create_text_channel("🚨﹒announcements", category=official_things)
        official_links = await guild.create_text_channel("🔗﹒official-links", category=official_things)
        roadmap = await guild.create_text_channel("🗺️﹒roadmap", category=official_things)
        giveaways = await guild.create_text_channel("🎁﹒giveaways", category=official_things)
        tweets = await guild.create_text_channel("🐤﹒tweets", category=official_things)
        await guild.edit(rules_channel=rules_chan, system_channel=announcements)



        general_chan = await guild.create_text_channel("💬﹒general", category=general)
        mh = await guild.create_text_channel("🧠﹒mental-health", category=general)
        questions = await guild.create_text_channel("❓﹒questions", category=general)
        suggestions = await guild.create_text_channel("📬﹒suggestions", category=general)
        scam = await guild.create_text_channel("🚨﹒scam-report", category=general)        
        
        g1 = await guild.create_voice_channel("General", category=voice_chats)
        g2 = await guild.create_voice_channel("General 2", category=voice_chats)
        g3 = await guild.create_voice_channel("General 3", category=voice_chats)

        chinese = await guild.create_text_channel("🇨🇳﹒chinese", category=languages)
        dutch = await guild.create_text_channel("🇳🇱﹒dutch", category=languages)
        filipinio = await guild.create_text_channel("🇵🇭﹒filipino", category=languages)
        german = await guild.create_text_channel("🇩🇪﹒german", category=languages)
        portugese = await guild.create_text_channel("🇧🇷﹒portuguese", category=languages)
        spanish = await guild.create_text_channel("🇪🇸﹒spanish", category=languages)

        help = await guild.create_text_channel("🆘﹒help", category=support)

        await ctx.respond("Categories and channels created\n")



        await ctx.send("Would you like to keep these channels and roles?")
        await ctx.send("If you do not confirm with 'yes', the setup will be undone in 30 seconds.")
        await ctx.send("Any other input will undo /setup")
        try:
            input = await self.bot.wait_for("message", timeout=30)
            if(input.content == 'yes') :
                undo = False
            else:
                undo = True
        except:
            undo = True

        
        # to remove roles, channels, and categories(for testing)
        ######################
        if undo:
            await ctx.respond("Deleting categories and channels")

            await core_chan.delete()
            await mod_chat.delete()
            await bot_commands.delete()
            
            await verification.delete()
            
            await rules_chan.delete()
            await announcements.delete()
            await official_links.delete()
            await roadmap.delete()
            await giveaways.delete()
            await tweets.delete()

            await general_chan.delete()
            await mh.delete()
            await questions.delete()
            await suggestions.delete()
            await scam.delete()

            await g1.delete()
            await g2.delete()
            await g3.delete()

            await chinese.delete()
            await dutch.delete()
            await filipinio.delete()
            await german.delete()
            await portugese.delete()
            await spanish.delete()

            await help.delete()


            await team.delete()
            await official_things.delete()
            await general.delete()
            await voice_chats.delete()
            await languages.delete()
            await support.delete()
            await start_here.delete()


            await ctx.send("deleting roles")
            role_object = discord.utils.get(guild.roles, name="Core")
            await role_object.delete()
            role_object = discord.utils.get(guild.roles, name="Lead Mods")
            await role_object.delete()
            role_object = discord.utils.get(guild.roles, name="Mods")
            await role_object.delete()
            role_object = discord.utils.get(guild.roles, name="Verified")
            await role_object.delete()

        #######################


    @setup.error
    async def example_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("Sorry {}, you do not have permissions to do that!".format(ctx.author.display_name))
        else:
            await ctx.respond("An error occured.")
            print(error)

    

def setup(bot):
    bot.add_cog(Setup(bot))
    