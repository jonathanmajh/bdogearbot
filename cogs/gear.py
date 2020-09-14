import os
import discord
from discord.ext import commands
from processing import add_gear, get_gear, get_average, get_all


class GearCog(commands.Cog, name='Gear'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gearadd')
    async def add_any_gear(self, ctx, gear_type='pve'):
        """
        Update your gear, default gear type is pve

        Available gear types: kutum, nouver, pvp, pve, dp-focus, evasion, ap-focus
        """
        gear_data = add_gear(gear_type, ctx)
        if gear_data.status:
            gear_data = gear_data.gear_data
            response = f'{gear_type} saved for {ctx.author.display_name}. {gear_data.succ_ap}/{gear_data.awak_ap}/{gear_data.dp}: GS: {gear_data.gs}'
        else:
            response = gear_data.message
        await ctx.send(response)

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

    @commands.command(name='gearaverage', help='Get the average GS of the guild')
    async def guild_average(self, ctx, gear_type=None):
        result = get_average(ctx.guild.id, gear_type)
        if result.status:
            response = f'Guild GS Average is: {result.message}'
        else:
            response = result.message
        await ctx.send(response)

    @commands.command(name='gearall', help='Get the GS of everyone in the guild')
    async def guild_all(self, ctx, gear_type=None):
        result = get_all(ctx.guild.id, gear_type)
        if result.status:
            response = f'''
```\nGear for all {ctx.guild.name} members are listed below
__________________________________________________________________
|Gear Type| GS  | AP  | AAP | DP  |  Updated   | Family Name'''
            for result in result.obj:
                response = f'''{response}
|{result.gear_type.ljust(9)}| {result.gs} | {result.succ_ap} | {result.awak_ap} | {result.dp} | {result.datestamp} | {result.family_name}'''
            response = f'{response}```'
        else:
            response = result.message
        await ctx.send(response)


def setup(bot):
    bot.add_cog(GearCog(bot))
