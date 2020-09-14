# bot.py
import os
import discord
import random
import time
import subprocess
from dotenv import load_dotenv

from discord.ext import commands, tasks

from database import create_connection, table_check, update_gear, find_gear
from models import GearData
from processing import add_gear, get_gear, get_average, get_all

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
HOME_PATH = os.getenv('HOME_PATH')
DB_PATH = f'{HOME_PATH}gear_bot_db.db'
version = subprocess.check_output(
    ["git", "describe", "--always"]).strip().decode()

initial_extensions = ['cogs.fun']

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


@bot.command(name='nouver', help='Updates your gear with nouver sub-weapon')
async def add_gear_nouver(ctx):
    gear_data = add_gear('nouver', ctx)
    if gear_data.status:
        gear_data = gear_data.gear_data
        response = f'Nouver saved for {ctx.author.display_name}. {gear_data.succ_ap}/{gear_data.awak_ap}/{gear_data.dp}: GS: {gear_data.gs}'
    else:
        response = gear_data.message
    await ctx.send(response)


@bot.command(name='kutum', help='Updates your gear with kutum sub-weapon')
async def add_gear_kutum(ctx):
    gear_data = add_gear('kutum', ctx)
    if gear_data.status:
        gear_data = gear_data.gear_data
        response = f'Kutum saved for {ctx.author.display_name}. {gear_data.succ_ap}/{gear_data.awak_ap}/{gear_data.dp}: GS: {gear_data.gs}'
    else:
        response = gear_data.message
    await ctx.send(response)


@bot.command(name='gear', help='Shows gear for member "~gear @Name" [nouver/kutum]')
async def retrive_gear(ctx, user_id, gear_type: str = None):
    if len(ctx.message.mentions) == 1:
        gear_data = get_gear(ctx.message.mentions[0].id, gear_type)
        if gear_data.status:
            if len(gear_data.photos) == 1:
                await ctx.send(gear_data.message, file=discord.File(gear_data.photos[0]))
            else:
                await ctx.send(gear_data.message, files=[
                    discord.File(gear_data.photos[0]),
                    discord.File(gear_data.photos[1]),
                ])
            return True
        else:
            response = gear_data.message
    else:
        response = 'Please @Member to get their gear'
    await ctx.send(response)


@bot.command(name='gearaverage', help='Get the average GS of the guild')
async def guild_average(ctx, gear_type=None):
    result = get_average(ctx.guild.id, gear_type)
    if result.status:
        response = f'Guild GS Average is: {result.message}'
    else:
        response = result.message
    await ctx.send(response)


@bot.command(name='gearall', help='Get the GS of everyone in the guild')
async def guild_all(ctx, gear_type=None):
    result = get_all(ctx.guild.id, gear_type)
    if result.status:
        response = f'''
```\nGear for all {ctx.guild.name} members are listed below
__________________________________________________________________
|Gear Type| GS  | AP  | AAP | DP  |  Updated   | Family Name'''
        for result in result.obj:
            response = f'''{response}
| {result.gear_type.ljust(8)}| {result.gs} | {result.succ_ap} | {result.awak_ap} | {result.dp} | {result.datestamp} | {result.family_name}'''
        response = f'{response}```'
    else:
        response = result.message
    await ctx.send(response)


@bot.command(name='gearinit')
async def init_function(ctx):
    if await bot.is_owner(ctx.author):
        response = 'initializing...'
        table_check()
    else:
        response = "🤔 You aren't my mom you can't tell me what to do! 😡"
    await ctx.send(response)

# wday, hour, minute in UTC 15 min early
GARMOTH_SCHEDULE = [[2, 3, 0], [4, 3, 0], [6, 23, 45]]


@tasks.loop(seconds=60.0)
async def boss_nagging():
    time_now = time.gmtime()
    for spawn in GARMOTH_SCHEDULE:
        if time_now.tm_wday == spawn[0]:
            if time_now.tm_hour == spawn[1]:
                if time_now.tm_min == spawn[2]:
                    channel = bot.get_channel(715760182201679883)
                    message = '<@!150050397883596800> Garmoth in 15 minutes CTG when?????'
                    await channel.send(message)

bot.run(TOKEN, bot=True, reconnect=True)
