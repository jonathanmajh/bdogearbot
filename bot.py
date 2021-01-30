# bot.py
import os
import subprocess

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
HOME_PATH = os.getenv('HOME_PATH')
DB_PATH = f'{HOME_PATH}gear_bot_db.db'
DEBUG = os.getenv('DEBUG')

version = subprocess.check_output(
    ["git", "describe", "--always"]).strip().decode()

initial_extensions = ['cogs.fun', 'cogs.gear', 'cogs.gamble',
                      'cogs.admin', 'cogs.bosstimer', 'cogs.items', 'cogs.error_handler']


if DEBUG:
    prefix = '~'
else:
    prefix = '?'
bot = commands.Bot(command_prefix=prefix,
                   description=f'BDOBot:\nAutomagically read GS from gear photos.\nGet item info and MP prices.\nWorld boss reminders\nv:{version}')
bot.owner_id = 152611107633233920

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print("The bot is connected to the following guilds:")
    for guild in bot.guilds:
        print("{} : {}".format(guild.name, guild.id))
    await bot.change_presence(activity=discord.Game('Black Spirit Notice Me!'))
    # await boss_nagging.start() no nagging for now


bot.run(TOKEN, bot=True, reconnect=True)
