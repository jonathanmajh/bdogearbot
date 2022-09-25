# bot.py
import os
import subprocess
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv
from typing import Union

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
HOME_PATH = os.getenv('HOME_PATH')
DB_PATH = f'{HOME_PATH}gear_bot_db.db'
DEBUG = os.getenv('DEBUG')

version = subprocess.check_output(
    ["git", "describe", "--always"]).strip().decode()

description=f'BDOBot:\nAutomagically read GS from gear photos.\nGet item info and MP prices.\nWorld boss reminders\nv:{version}'

if DEBUG:
    prefix = '~'
else:
    prefix = '?'

owner_id = 152611107633233920

initial_extensions = ['cogs.fun', 'cogs.gear']

bot = commands.Bot(command_prefix=prefix, description=description, owner_id=owner_id, intents=intents)

@bot.event
async def on_ready():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.')
            print(e)

    await bot.tree.sync()
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    for guild in bot.guilds:
        print("{} : {}".format(guild.name, guild.id))
        await bot.change_presence(activity=discord.Game('Black Spirit Notice Me!'))
    print('------')

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.tree.command(name='bot')
async def bot_info(interaction: discord.Interaction, ):
    """Is the bot cool?"""
    await interaction.response.send_message('Yes, the bot is cool.')

@bot.tree.command(name='channel-info')
@discord.app_commands.describe(channel='The channel to get info of')
async def channel_info(interaction: discord.Interaction, channel: Union[discord.VoiceChannel, discord.TextChannel]):
    """Shows basic channel info for a text or voice channel."""

    embed = discord.Embed(title='Channel Info')
    embed.add_field(name='Name', value=channel.name, inline=True)
    embed.add_field(name='ID', value=channel.id, inline=True)
    embed.add_field(
        name='Type',
        value='Voice' if isinstance(channel, discord.VoiceChannel) else 'Text',
        inline=True,
    )

    embed.set_footer(text='Created').timestamp = channel.created_at
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)


# initial_extensions = ['cogs.fun', 'cogs.gear', 'cogs.gamble',
#                       'cogs.admin', 'cogs.items', 'cogs.error_handler']


# bot = commands.Bot(command_prefix=prefix,
#                    description=f'BDOBot:\nAutomagically read GS from gear photos.\nGet item info and MP prices.\nWorld boss reminders\nv:{version}')
# bot.owner_id = 152611107633233920

# if __name__ == '__main__':
#     for extension in initial_extensions:
#         try:
#             bot.load_extension(extension)
#         except Exception as e:
#             print(f'Failed to load extension {extension}.')
#             print(e)

# @bot.event
# async def on_ready():
#     print(f'{bot.user.name} has connected to Discord!')
#     print("The bot is connected to the following guilds:")
#     for guild in bot.guilds:
#         print("{} : {}".format(guild.name, guild.id))
#     await bot.change_presence(activity=discord.Game('Black Spirit Notice Me!'))
#     # await boss_nagging.start() no nagging for now

# bot.run(TOKEN, bot=True, reconnect=True)
