import os
import shutil

import discord
from bin.database import add_server, reset_server_requests, table_check
from bin.models import ServerInfo
from discord.ext import commands

from cogs.error_handler import CommandErrorHandler


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='init', hidden=True)
    @commands.is_owner()
    async def init_function(self, ctx):
        table_check()
        await ctx.send('bot initialized')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send('Hello There...\nPlease tell a manager to set me up by running ?setup')
            break

    @commands.command(name='setup')  # TODO change to seperate messages
    async def setup_server(self, ctx, *, args=None):
        """
        Function to setup bot when first joining a server
        """
        if args == None:
            response = '''
```The following information is optional:
general="general-channel-name"
Channel where boss reminder messages will be sent\n
photo="gear-photo-channel-name"
Channel where only gear photos will be posted, bot will not respond to another other command in this channel\n
Ex. "?setup general=guild-general photo=gear-photo"
Ex. "?setup default"'
```'''
        elif args == 'default':
            server_info = ServerInfo(
                server_id=ctx.guild.id, server_owner=ctx.author.id)
            for channel in ctx.guild.text_channels:
                if channel.permissions_for(ctx.guild.me).send_messages:
                    server_info.general_channel_id = channel.id
                    break
            result = add_server(server_info)
            response = 'Finished server setup'
        else:
            response = 'unimplimented (:'
        await ctx.send(response)

    @commands.command(name='maint', hidden=True)
    @commands.is_owner()
    async def maintenance(self, ctx, state):  # start/end
        await self.bot.change_presence(activity=discord.Game('Currently Undergoing Maintence!'))
        await ctx.send('Starting maintence mode...\nUnloading extensions...')
        self.bot.unload_extension('cogs.fun')
        self.bot.unload_extension('cogs.gear')
        await ctx.send('Extensions unloaded...\nNow backing up data...')
        source_dir = os.getenv('HOME_PATH')
        dest_dir = f'{source_dir[:-11]}backup/'
        shutil.rmtree(dest_dir, ignore_errors=True)
        os.mkdir(dest_dir)
        shutil.copy(f'{source_dir}gear_bot_db.db', f'{dest_dir}gear_bot_db.db')
        shutil.copytree(f'{source_dir}screenshots/', f'{dest_dir}screenshots/')
        await ctx.send('Finished backing up data...\nMaintence prep finished!')

    @commands.command(name='resetlimit', hidden=True)
    @commands.is_owner()
    async def reset_limit(self, ctx, new_limit: int):  # int
        await self.bot.change_presence(activity=discord.Game('Resetting the rate limit for everyone <3'))
        reset_server_requests(new_limit)
        await ctx.send(f'Reset remaining requests for all guilds to {new_limit}')
        await self.bot.change_presence(activity=discord.Game('Black Spirit Notice Me!'))

    @commands.command(name='senderror', hidden=True)
    @commands.is_owner()
    async def send_error(self, ctx, message: str = 'testing'):  # int
        CommandErrorHandler().send_pm(error=error)
        raise Exception('message')


def setup(bot):
    bot.add_cog(AdminCog(bot))
