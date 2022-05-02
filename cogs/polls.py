import asyncio
from email import message
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from datetime import datetime, timedelta


class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    @commands.has_permissions(manage_webhooks=True)
    @commands.slash_command(name="poll",
                            description="Create a poll. Max of 10 options")
    async def poll(self, ctx: Context, text_channel, number_of_options):
        number_of_options = int(number_of_options)
        chID_stripped = text_channel[2:]
        chID_stripped = chID_stripped[:-1]
        ch = self.bot.get_channel(int(chID_stripped))

        if number_of_options > 10:
            await ctx.respond('Cannot have more than 10 options')
            return
        def check(m):
            return m.content and m.channel == ctx.channel
        options = list()
        for i in range(number_of_options):
            await ctx.respond(f'Respond with option {i+1}:')
            try:
                response = await self.bot.wait_for("message", check=check, timeout=120)
            except asyncio.TimeoutError:
                await ctx.respond('You took too long to respond to the message (Timeout after 2 minutes).')
            options.append(response.content)
        await ctx.respond('How long would you like the poll to run for?\nEnter in one of the following formats:\n'
                          '[1s, 1m, 1h, 1d]')
        try:
            time = await self.bot.wait_for("message", check=check, timeout=120)
            time = time.content
        except asyncio.TimeoutError:
            await ctx.respond('You took too long to respond to the message (Timeout after 2 minutes).')

        # Find giveaway time
        time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        operand = time[-1].casefold()
        intTime = int(time[:-1])
        multiplier = int(time_convert.get(operand))
        poll_time = intTime * multiplier
        # find time poll ends
        dt = datetime.now()
        td = timedelta(seconds=poll_time)
        future = dt + td
        unixTimestamp = (datetime.timestamp(future))
        unixTimestamp = int(unixTimestamp)

        # emojis 1-10
        emojis = [
            "1\ufe0f\u20e3",
            "2\ufe0f\u20e3",
            "3\ufe0f\u20e3",
            "4\ufe0f\u20e3",
            "5\ufe0f\u20e3",
            "6\ufe0f\u20e3",
            "7\ufe0f\u20e3",
            "8\ufe0f\u20e3",
            "9\ufe0f\u20e3",
            "\U0001F51F"
        ]

        embed = discord.Embed(title="Poll! :bar_chart:", color=discord.Color.dark_purple(),)
        embed.add_field(name="React with corresponding number to vote!", value="\u200b", inline=True)
        for i in range(number_of_options):
            embed.add_field(name=f'{emojis[i]} :', value=options[i], inline=False)
        embed.add_field(name=f'Length of poll: {time.casefold()}',
                        value=f'Poll ends: <t:{unixTimestamp}:f>\n(<t:{unixTimestamp}:R>)', inline=True)
        poll_msg = await ch.send(embed=embed)
        await ctx.respond('Poll sent to designated text-channel!')
        for i in range(number_of_options):
            await poll_msg.add_reaction(emojis[i])

        await asyncio.sleep(intTime)
        cache_msg = await ch.fetch_message(poll_msg.id)
        await self.end_poll(cache_msg, embed, time, ch)

    async def end_poll(self, message, embed, time, channel):
        print(message.reactions)

        embed.set_field_at(0, name="Results:", value="\u200b", inline=False)
        embed.set_field_at(len(embed.fields)-1, name=f'Length of poll: {time.casefold()}', value = "Poll has ended.", inline=False)
        for i in range(len(message.reactions)):
            val = embed.fields[i+1].value
            embed.set_field_at(i+1, name=f'{val} :  ', value=f'{str(message.reactions[i].count - 1)} votes', inline=False)
        await message.edit(embed = embed)
        await message.clear_reactions()


def setup(bot):
    bot.add_cog(Polls(bot))
