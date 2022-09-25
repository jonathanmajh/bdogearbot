# bot.py
import os
import subprocess

import discord
from discord.ext import commands
from dotenv import load_dotenv

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

description=f'BDOBot:\nAutomagically read GS from gear photos.\nv:{version}'

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

bot.run(TOKEN)