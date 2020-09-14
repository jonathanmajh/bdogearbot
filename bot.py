# bot.py
import os
import discord
import subprocess
from dotenv import load_dotenv

from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
HOME_PATH = os.getenv('HOME_PATH')
DB_PATH = f'{HOME_PATH}gear_bot_db.db'
version = subprocess.check_output(
    ["git", "describe", "--always"]).strip().decode()

initial_extensions = ['cogs.fun', 'cogs.gear', 'cogs.admin']

bot = commands.Bot(command_prefix='~',
                   description=f'BDOGearBot: Automagically read GS from gear photos. v:{version}')
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
