import os
from datetime import datetime
from random import choice

import discord
from bin.database import add_server_message, get_server_message
from discord.ext import commands, tasks


class ForFunCog(commands.Cog, name='4FUNctions'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Ping a random member for a hug, only pings online members', aliases=['trees'])
    async def hug(self, ctx):
        members = ctx.guild.members
        found = False
        while not found:
            found = choice(members)
            if found.status.value != 'online' or found.bot:
                found = False
        if choice(range(100)) > 90:
            response = f'{ctx.author.display_name} was griefing a guildie! 😲 <@!{found.id}> go show them their place! 😡'
        else:
            response = f'{ctx.author.display_name} is feeling sad 😥 <@!{found.id}> can you give them a hug? 🤗 Or maybe doing trees with them is better 🤑'
        await ctx.send(response)

    @commands.command(aliases=['e'], help='Send a BDO Emote "?e emote_name"')
    async def emote(self, ctx, emote_name: str):
        emote_path = f"{os.getenv('HOME_PATH')}assets/emotes/{emote_name}.gif"
        if os.path.isfile(emote_path):
            await ctx.send(file=discord.File(emote_path))
        else:
            await ctx.send('That emote does not exist, make sure you are using the same name as BDO but with all lowercase')

    @commands.command(aliases=['expose', 'gm'])
    async def guild(self, ctx, *, arg=None):
        """
        Send a scathing message about the guild

        ?guild list to show all messages
        """
        if arg == None:
            result = get_server_message(ctx.guild.id, False)
            if result:
                response = f'```{result[0][0]}```'
            else:
                response = 'There are no saved messages'
        elif arg == 'list' or arg == 'listd':
            response = '```'
            messages = get_server_message(ctx.guild.id, True)
            if messages:
                for message in messages:
                    if arg == 'list':
                        response = f'{response}{message[0]}\n'
                    else:
                        response = f'{response}{message[0]}|{message[1]}\n'
                response = f'{response}```'
            else:
                response = 'There are no saved messages'
        else:
            add_server_message(ctx.guild.id, arg, ctx.author.id)
            response = f'```{arg}``` has been added for this Guild'
        await ctx.send(response)

    @tasks.loop(seconds=5)
    async def daily_message(self):
        print('daily message')
        if datetime.now().tm_hour == 13:
            result = get_server_message(715760181832843344, False)
            if result:
                response = f'```{result[0][0]}```'
                channel = self.bot.get_channel(285232745150677013) #TODO change
                await channel.send(response)

    @daily_message.before_loop
    async def before_daily(self):
        print('waiting...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(ForFunCog(bot))
