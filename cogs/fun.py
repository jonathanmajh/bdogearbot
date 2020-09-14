import os
import discord
from discord.ext import commands
from database import add_server_message, get_server_message


class ForFunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['e'], help='Send a BDO Emote "?e emote_name"')
    async def emote(self, ctx, emote_name: str):
        emote_path = f"{os.getenv('HOME_PATH')}assets/emotes/{emote_name}.gif"
        if os.path.isfile(emote_path):
            await ctx.send(file=discord.File(emote_path))
        else:
            await ctx.send(message='That emote does not exist, make sure you are using the same name as BDO but with all lowercase')

    @commands.command(aliases=['expose'])
    async def guild(self, ctx, *, arg):
        """
        Send a scathing message about the guild

        ?guild list to show all messages
        """
        if arg == None:
            response = f'```{get_server_message(ctx.guild.id, False)[0]}```'
        elif arg == 'list':
            response = '```'
            messages = get_server_message(ctx.guild.id, True)
            for message in messages:
                response = f'{response}{message}\n'
            response = f'{response}```'
        else:
            add_server_message(ctx.guild.id, arg)
            response = f'{arg} has been added for this Guild'
        await ctx.send(message=response)


def setup(bot):
    bot.add_cog(ForFunCog(bot))
