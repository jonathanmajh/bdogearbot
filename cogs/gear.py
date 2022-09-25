import asyncio
import os
from math import ceil
import typing

import discord
from bin.processing import (add_gear, get_all, get_average, get_gear,
                            remove_gear, get_id)
from discord.ext import commands
from discord.utils import get
from cogs.admin import check_admin


class GearCog(commands.Cog, name='Gear'):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='gear')
    async def gear(self, ctx, attachment: typing.Optional[discord.Attachment], user: typing.Optional[discord.User]):
        """
        ?gear to see your own gear
        ?gear [photo] to update your gear
        ?gear [@member] to see someone else's gear
        """
        
        if attachment is not None:
            message = ''
            gear_data = add_gear('gear', ctx, attachment)
            if gear_data.status:
                message = gear_data.message
                gear_data = gear_data.gear_data
                response = f'gear saved for {ctx.author.display_name}. {gear_data.succ_ap}/{gear_data.awak_ap}/{gear_data.dp}: GS: {gear_data.gs}\n'
            else:
                response = gear_data.message
                if gear_data.obj:
                    error_handler = self.bot.get_cog('CommandErrorHandler')
                    await error_handler.send_pm(gear_data.obj)
            response = response + (message if message else '')
            await ctx.send(response)
        else:
            user_id = 0
            if user is not None:
                user_id = user.id
            else:
                user_id = ctx.author.id
            gear_data = get_gear(user_id, 'gear')
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
                await ctx.send(gear_data.message)
            

    @commands.hybrid_command(name='purge')
    async def remove_deserter_gear(self, ctx, id:int):
        """
        Remove gear of a member who left using their discord id
        Will send a confirmation message
        """
        if not check_admin(ctx):
            await ctx.send("You are not admin of this server! :anger:")
            return True
        channel = ctx.message.channel
        user = self.bot.get_user(id)
        if not user:
            message = f"You are deleting gear. React to confirm"
        else:
            message = f"You are deleting {user.name}'s gear. React to confirm"
        message = await channel.send(message)
        await message.add_reaction('💯')
        await message.add_reaction('🛑')

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == '💯' or str(reaction.emoji) == '🛑')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await channel.send(f'Gear remove for cancelled (60s timeout exceeded)')
        else:
            await channel.send(f'you reacted with {reaction.emoji}')
            print('removing gear')
            result = remove_gear(id, 'all')
            await channel.send(result.message)

    @commands.hybrid_command(name='gearremove', aliases=['grm'])
    async def remove_any_gear(self, ctx):
        """
        Remove your gear
        Will send a confirmation message
        """
        gear_type='all'
        channel = ctx.message.channel
        message = await channel.send(f'You are deleting your gear. React to confirm')
        await message.add_reaction('💯')
        await message.add_reaction('🛑')

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == '💯' or str(reaction.emoji) == '⁉')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await channel.send(f'Gear remove for {ctx.author.display_name} cancelled (60s timeout exceeded)')
        else:
            await channel.send(f'you reacted with {reaction.emoji}')
            print('removing gear')
            result = remove_gear(ctx.author.id, gear_type)
            await channel.send(result.message)

    @commands.hybrid_command(name='gearaverage')
    async def guild_average(self, ctx, gear_type=None):
        """Get the average GS of the guild"""
        result = get_average(ctx.guild.id, gear_type)
        if result.status:
            response = f'Guild GS Average is: {format(result.message, ".1f")}'
        else:
            response = result.message
        await ctx.send(response)

    @commands.hybrid_command(name='gearall')
    async def guild_all(self, ctx, page='1', gear_type=None):
        """Get the GS of everyone in the guild"""
        temp = page
        try: # incase user flips the parameters
            page = int(page)
        except ValueError:
            if gear_type:
                page = int(gear_type)
            else:
                page = 1
            gear_type = temp
        results = get_all(ctx.guild.id, gear_type, page-1)
        if results.status:
            response = f'''
```\nGear for all {ctx.guild.name} members are listed below
__________________________________________________________________
|Gear Type| GS  | AP  | AAP | DP  |  Updated   | Family Name'''
            for result in results.obj:
                response = f'''{response}
|{result.gear_type.ljust(9)}| {result.gs} | {result.succ_ap} | {result.awak_ap} | {result.dp} | {result.datestamp} | {result.family_name}'''
            response = f'''{response}
Page {page} of {ceil(results.code / 10)}: ({results.code} Entries)```'''
        else:
            response = results.message
        await ctx.send(response)


    @commands.hybrid_command(name='gearid')
    async def guild_id(self, ctx, page='1'):
        """Get the ID & Family Name of everyone with gear in the guild"""
        try: # incase user flips the parameters
            page = int(page)
        except ValueError:
            page = 1
        results = get_id(ctx.guild.id, page-1)
        if results.status:
            response = f'''
```\nFamily Name and ID for all {ctx.guild.name} members are listed below
__________________________________________________________________
|        ID        | Family Name'''
            for result in results.obj:
                response = f'''{response}
|{str(result.user_id).ljust(18)}| {result.message}'''
            response = f'''{response}
Page {page} of {ceil(results.code / 20)}: ({results.code} Entries)```'''
        else:
            response = results.message
        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(GearCog(bot))
