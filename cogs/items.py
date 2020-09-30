import discord
import asyncio
import re
from discord.ext import commands

from scraper import get_item_info, get_mp_info
from item_processing import combo_search, get_enchant_lvl, format_item_info, format_mp_info


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
        query = arg.strip()
        split_query = query.split()
        enchant = get_enchant_lvl(split_query[-1])
        enchant_lvl = enchant.code
        enchant = enchant.status
        if split_query[0].isdigit() and ((len(split_query) == 2 and enchant) or len(split_query) == 1):
            print(split_query)
            item = get_item_info(split_query[0], enchant_lvl)
            if item.status:
                item = item.obj
                message = format_item_info(item)
                message_send = f'{message}Loading Marketplace Information...```'
                msg = await ctx.send(message_send)
                mp = get_mp_info(item)
                message_mp = format_mp_info(mp)
                message_send = f'{message}{message_mp}'
                await msg.edit(content=message_send)
            else:
                await ctx.send(item.message)
        else:
            if enchant:
                query = ' '.join(split_query[:-1])
            result = combo_search(query)
            if result.status:
                if len(result.obj) == 1:
                    item = get_item_info(result.obj[0][0], enchant_lvl)
                    if item.status:
                        item = item.obj
                        message = format_item_info(item)
                        message_send = f'{message}Loading Marketplace Information...```'
                        msg = await ctx.send(message_send)
                        mp = get_mp_info(item)
                        message_mp = format_mp_info(mp)
                        message_send = f'{message}{message_mp}'
                        await msg.edit(content=message_send)
                else:
                    response = f'''
```{result.message}
| Item ID | Item Name'''
                    for result in result.obj:
                        response = f'''{response}
|{str(result[0]).ljust(9)}| {result[1]}'''
                    response = f'{response}```'
                    await ctx.send(response)
            else:
                response = result.message
                await ctx.send(response)


def setup(bot):
    bot.add_cog(ItemCog(bot))
