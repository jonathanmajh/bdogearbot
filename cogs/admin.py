import discord
from discord.ext import commands
from database import table_check, add_server
from models import ServerInfo

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

    @commands.command(name='setup')
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
            server_info = ServerInfo(server_id=ctx.guild.id, server_owner=ctx.author.id)
            for channel in ctx.guild.text_channels:
                if channel.permissions_for(ctx.guild.me).send_messages:
                    server_info.general_channel_id = channel.id
                    break
            result = add_server(server_info)
            response = 'Finished server setup'
        else:
            response = 'unimplimented (:'
        await ctx.send(response)


def setup(bot):
    bot.add_cog(AdminCog(bot))