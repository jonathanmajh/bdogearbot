import discord
import asyncio
import re
from discord.ext import commands

from item_processing import combo_search, get_enchant_lvl

class ItemCog(commands.Cog, name='Items'):
    def __init__(self, bot):
        self.bot = bot
        self.persist = 0

    @commands.command(name='item')
    async def item_search(self, ctx, *, arg=None):
        """
        Look up BDO items by name

        Returns item information and marketplace price if only one match is found
        
        Item enhancement levels can be added to the end

        Some items, knowledge, NPCs share the same name. 
        Please use the item id to specify the exact item
        Example usage:
        ?item kzarka staff
        ?item kzarka staff +19
        ?item kzarka staff V
        ?item 14410 ii
        """
        if arg == None:
            await ctx.send("Please enter a search term")
            return 0
        query = arg.lower().strip()
        split_query = split(query)
        enchant = get_enchant_lvl(split_query[-1])
        enchant_lvl = enchant.code
        enchant = enchant.status
        if len(split_query) <= 2 and split_query[0].isdigit():
            pass # get market and item data
        else:
            if enchant:
                query = ' '.join(split_query[:-1])
            result = combo_search(query)
        if result.status:
            if len(result.obj) == 1:
                # post request to bdocodex to get item details
            else:
                response = f'''
```{result.message}
| Item ID | Item Name'''
                for result in result.obj:
                    response = f'''{response}
|{result[0].ljust(9)}|{result[1]}'''
                response = f'{response}```'
        else:
            response = result.message
        await ctx.send(response)


def setup(bot):
    bot.add_cog(ItemCog(bot))