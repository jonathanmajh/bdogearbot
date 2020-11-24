import asyncio
import os
from math import ceil

import discord
from bin.processing import (add_gear, get_all, get_average, get_gear,
                            remove_gear)
from discord.ext import commands
from discord.utils import get


class GearCog(commands.Cog, name='Gear'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gearadd', aliases=['ga'])
    async def add_any_gear(self, ctx, gear_type='pve'):
        """
        Update your gear, default gear type is pve

        Suggested gear types: kutum, nouver, pvp, pve, dp-focus, evasion, ap-focus

        gear type cannot be longer than 9 characters
        """
        if len(gear_type) > 9:
            await ctx.send('specified gear type is longer than 9 characters')
        else:
            message = ''
            gear_data = add_gear(gear_type, ctx)
            if gear_data.status:
                message = gear_data.message
                gear_data = gear_data.gear_data
                response = f'{gear_type} saved for {ctx.author.display_name}. {gear_data.succ_ap}/{gear_data.awak_ap}/{gear_data.dp}: GS: {gear_data.gs}\n'
            else:
                response = gear_data.message
                error_handler = self.bot.get_cog('CommandErrorHandler')
                await error_handler.send_pm(gear_data.obj)
            response = response + (message if message else '')
            await ctx.send(response)

    @commands.command(name='gearremove', aliases=['grm'])
    async def remove_any_gear(self, ctx, gear_type='all'):
        """
        Remove your gear, by default removes your all entries

        Specify a gear type to remove only one entry

        Will send a confirmation message
        """

        channel = ctx.message.channel
        if gear_type == 'all':
            message = await channel.send("You are deleting all your gear. React to confirm")
        else:
            message = await channel.send(f'You are deleting your {gear_type} gear. React to confirm')
        await message.add_reaction('💯')
        await message.add_reaction('⁉')

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

    @commands.command(name='nouver')
    async def add_gear_nouver(self, ctx):
        """Shortcut for ?gearadd nouver"""
        await self.add_any_gear(ctx, 'nouver')

    @commands.command(name='kutum')
    async def add_gear_kutum(self, ctx):
        """Shortcut for ?gearadd kutum"""
        await self.add_any_gear(ctx, 'kutum')

    @commands.command(name='gear', help='Shows gear for member "~gear @Name" [nouver/kutum]')
    async def retrive_gear(self, ctx, user_id, gear_type: str = None):
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

    @commands.command(name='gearaverage', aliases=['gavg'], help='Get the average GS of the guild')
    async def guild_average(self, ctx, gear_type=None):
        result = get_average(ctx.guild.id, gear_type)
        if result.status:
            response = f'Guild GS Average is: {format(result.message, ".1f")}'
        else:
            response = result.message
        await ctx.send(response)

    @commands.command(name='gearall', help='Get the GS of everyone in the guild')
    async def guild_all(self, ctx, page=1, gear_type=None):
        temp = page
        try: # incase user flips the parameters
            page = int(page)
        except ValueError:
            page = int(gear_type)
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


def setup(bot):
    bot.add_cog(GearCog(bot))
