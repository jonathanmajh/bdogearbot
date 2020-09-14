import os
import discord
from discord.ext import commands
from processing import add_gear

class GearCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add_gear_nouver(self, ctx):
        gear_data = add_gear('nouver', ctx)
        if gear_data.status:
            gear_data = gear_data.gear_data
            response = f'Nouver saved for {ctx.author.display_name}. {gear_data.succ_ap}/{gear_data.awak_ap}/{gear_data.dp}: GS: {gear_data.gs}'
        else:
            response = gear_data.message
        await ctx.send(message=response)