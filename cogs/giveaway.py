import time
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import asyncio
import random
import textwrap
from api.data_handler import *



class giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    # This command creates a giveaway, converts the time, waits until the time is up, and selects a winner.
    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="create_giveaway", description="Start a giveaway with randomly selected winners")
    async def gcreate(self, ctx: Context):

        def check(m):
            return m.content and m.channel == ctx.channel
        try:
            await ctx.respond('How long would you like the giveaway to go for? Submit in the following format: [1s, 1m, 1h, 1d].')
            time_msg = await self.bot.wait_for("message", check=check, timeout=45)
            gtime = time_msg.content

            await ctx.respond('How many winners?')
            num_of_winners = await self.bot.wait_for("message", check=check, timeout=45)
            num_of_winners = num_of_winners.content

            await ctx.respond('What is the prize you will be giving away?')
            prize_msg = await self.bot.wait_for("message", check=check, timeout=45)
            prize = prize_msg.content

            await ctx.respond('What channel would you like the giveaway to be held in? Enter as #channel-name')
            channel_loc = await self.bot.wait_for("message", check=check, timeout=45)
            chID_stripped = channel_loc.content[2:]
            chID_stripped = chID_stripped[:-1]
            ch = self.bot.get_channel(int(chID_stripped))

            await ctx.respond('What channel would you like the giveaway winner list to be posted to?'
                              'This result contains no mentions and can be used for your own records.'
                              ' Enter as #channel-name')
            channel_loc = await self.bot.wait_for("message", check=check, timeout=45)
            chID_stripped = channel_loc.content[2:]
            chID_stripped = chID_stripped[:-1]
            chWIN = self.bot.get_channel(int(chID_stripped))
        except asyncio.TimeoutError:
            await ctx.respond('You took too long to respond! Please call the command again.')
            return
        except ValueError:
            await ctx.respond('An input error likely occured. Please call the command again.')
            return

        numOfWinners = int(num_of_winners)

        embed = discord.Embed(title=':gift: New Giveaway! :gift:', description=f'\n{ctx.author.mention} is giving away **{prize}**!!\n\n'
                                                                     'React with 🎉 to enter!!!\n\n', color=0xf1c40f)
        embed.add_field(name=':medal: Winners:', value=f'{numOfWinners}', inline=True)
        # Find giveaway time
        time_convert = {"s":1, "m":60, "h":3600,"d":86400}
        operand = gtime[-1].casefold()
        intTime = int(gtime[:-1])
        multiplier = int(time_convert.get(operand))
        gawtime = intTime * multiplier

        # Calculate time and date the giveaway ends
        dt = datetime.now()
        td = timedelta(seconds=gawtime)
        future = dt + td
        unixTimestamp = (datetime.timestamp(future))
        unixTimestamp = int(unixTimestamp)
        embed.add_field(name=f'Length of giveaway: {gtime.casefold()}', value=f'Giveaway ends: <t:{unixTimestamp}:f>\n(<t:{unixTimestamp}:R>)', inline=False)

        gaw_msg = await ch.send(embed=embed)
        self.send_to_file(gaw_msg.id, (future - datetime(1970, 1, 1)).total_seconds(), numOfWinners, prize, ch, chWIN)

        await gaw_msg.add_reaction("🎉")
        await asyncio.sleep(gawtime)

        await self.end_gaw(gaw_msg.id, numOfWinners, prize, ch, chWIN)

    def send_to_file(self, message_id, end_time, num_winners, prize, ch, chWIN):
        with open("data/giveaways.json", "r") as _:
            data = json.load(_)

            new_set = {
                "giveaway_id": message_id,
                "end_time": end_time,
                "num_winners": num_winners,
                "prize": prize,
                "terminated": False,
                "host_channel": ch.id,
                "winners_channel": chWIN.id,
            }

            if new_set not in data:
                data.append(new_set)

        with open("data/giveaways.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)
        with open("data/gaw_log.json", "r") as _:
            data = json.load(_)

            new_set = {
                "giveaway_id": message_id,
                "losers": " "
            }

            if new_set not in data:
                data.append(new_set)
        with open("data/gaw_log.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)

    async def check_for_active_giveaways(self, ctx: Context):
        # if giveaway time has not happened yet, reactivate.
        with open("data/giveaways.json", "r") as _:
            data = json.load(_)
            await asyncio.gather(*(self.reactivate_giveaway(item['giveaway_id'], item['end_time'],
                                                            item['num_winners'], item['prize'], item["host_channel"], item["winners_channel"]) for item in data))

    async def reactivate_giveaway(self, message_id, end_time, num_winners, currPrize, ch, chWIN):
        print(f"[Bot] Giveaway {message_id} of {currPrize} has been reactivated!")
        await asyncio.sleep(end_time-time.time())
        ch = self.bot.get_channel(ch)
        chWIN = self.bot.get_channel(chWIN)
        await self.end_gaw(message_id, num_winners, currPrize, ch, chWIN)

    async def end_gaw(self, message_id, num_winners, end_prize, ch, chWIN):
        new_gaw_msg = await ch.fetch_message(message_id)
        guild = new_gaw_msg.guild
        # get collection of users who reacted
        users = set()
        for reaction in new_gaw_msg.reactions:
            async for user in reaction.users():
                users.add(user)
        listUsers = list(users)
        listUsers.remove(new_gaw_msg.author)

        # Find the winners
        winners = list()
        for i in range(num_winners):
            tempWinner = random.choice(listUsers)
            winners.append(tempWinner)
            listUsers.remove(tempWinner)
        # write people who didn't win to JSON
        losers = list()
        for i in listUsers:
            losers.append(i.id)
        with open("data/gaw_log.json", "r") as _:
            data = json.load(_)
            for item in data:
                if item["giveaway_id"] == message_id:
                    item["losers"] = losers
        with open("data/gaw_log.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)

        for winner in winners:
            await new_gaw_msg.remove_reaction('🎉', winner)
        # get winners discord IDs
        winnerIDs = list()
        for i in range(num_winners):
            winnerIDs.append(winners[i].id)
        # get winners wallet addresses
        winnerWallets = list()
        for i in range(num_winners):
            winnerWallets.append(await get_input(guild.id, winnerIDs[i]))
        # format and print winners + wallet addresses
        winnerOutput = f'Winners of {end_prize}:\n'
        for i in range(num_winners):
            winnerOutput += f'{winners[i]} Wallet: {winnerWallets[i]}\n'
        winnerOutputNoWallet = f'Winners of {end_prize}:\n'
        for i in range(num_winners):
            winnerOutputNoWallet += f'{winners[i].mention}\n'

        numOfCharsInWinnerOutput = len(winnerOutput)
        numOfCharsInWinnerNoWallet = len(winnerOutputNoWallet)

        if numOfCharsInWinnerNoWallet >= 2000:
            lines = textwrap.wrap(winnerOutputNoWallet, 1900, break_long_words=False)
            mes = await ch.send(lines[0])  # Send winners to giveaway channel
            if guild.premium_tier > 1:
                private_thread = await mes.channel.create_thread(name=f'{end_prize} Giveaway Winners', type=None)
                await private_thread.send(lines[0])
            for i in lines[1:]:
                await ch.send(i)  # Send winners to giveaway channel
                if guild.premium_tier > 1:
                    await private_thread.send(lines[i])
        elif numOfCharsInWinnerOutput >= 2000:
            lines = textwrap.wrap(winnerOutput, 1900, break_long_words=False)
            for i in lines:
                await chWIN.send(i)
            if numOfCharsInWinnerNoWallet < 2000:
                mes = await ch.send(winnerOutputNoWallet)  # Send winners to giveaway channel
                if guild.premium_tier > 1:
                    private_thread = await mes.channel.create_thread(name=f'{end_prize} Giveaway Winners', type=None)
                    await private_thread.send(winnerOutputNoWallet)
        else:
            await chWIN.send(winnerOutput)  # Send winners and wallets to winners channel
            mes = await ch.send(winnerOutputNoWallet)  # Send winners to giveaway channel
            if guild.premium_tier > 1:
                private_thread = await mes.channel.create_thread(name=f'{end_prize} Giveaway Winners', type=None)
                await private_thread.send(winnerOutputNoWallet)
        update_embed = discord.Embed(title=f':gift: {end_prize} Giveaway Winners :gift:', description=f'{winnerOutputNoWallet}')
        update_embed.add_field(name='Giveaway ended:', value=f'<t:{int(datetime.timestamp(datetime.now()))}:R>')
        await new_gaw_msg.edit(embed=update_embed)

        await self.remove_from_json(message_id)

    async def remove_from_json(self, message_id):
        with open("data/giveaways.json", "r") as _:
            data = json.load(_)
            for item in data:
                if item["giveaway_id"] == message_id:
                    item["terminated"] = True
                    data.remove(item)
        with open("data/giveaways.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)


    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="reroll", description="Reroll a select # of giveaway winners. Call from giveaway channel")
    async def reroll(self, ctx: Context, message_id, number_of_rerolls):
        channel = ctx.channel
        guild = ctx.guild
        await ctx.respond("Rerolling.....", ephemeral=True)
        # get list of people who reacted to old giveaway
        entrants = list()
        with open("data/gaw_log.json", "r") as _:
            data = json.load(_)
            for item in data:
                if item["giveaway_id"] == int(message_id):
                    entrants = item["losers"]
        with open("data/gaw_log.json", "w") as _:
            json.dump(obj=data, fp=_, indent=4)

        # Find the winners
        winners = list()
        for i in range(len(number_of_rerolls)):
            tempWinner = random.choice(entrants)
            winners.append(tempWinner)
            entrants.remove(tempWinner)

        reroll_output = "Rerolled winners:\n"
        for winner in winners:
            new_win = await guild.fetch_member(winner)
            reroll_output += f"{new_win.mention}\n"
        await channel.send(reroll_output)



def setup(bot):
    bot.add_cog(giveaway(bot))