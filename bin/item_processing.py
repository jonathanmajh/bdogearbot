import locale
import re

import discord
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

from metaphone.metaphone import doublemetaphone

from bin.database import (get_item_by_id, item_exact_search, item_leven_search,
                          item_like_search, item_no_phone, item_phone_search)
from bin.models import ItemInfo, Result


def combo_search(query: str):
    """search for user's query"""
    query = query.replace("(", "").replace(")", "").replace("-", "").replace("'",
            "").replace(":", "").replace("[", "").replace("]", "").replace("/", " ").replace("  ", " ")
    result = item_exact_search(query)
    if len(result) > 0:
        return Result(True, message='Multiple matches found, please select using item ID (E)', obj=result)
    query = query.lower()
    result = item_like_search(query)
    if len(result) > 0:
        return Result(True, message='Multiple matches found, please select using item ID (L)', obj=result)
    dmp = doublemetaphone(query)
    if len(dmp[0]) != 0:
        result = item_phone_search(dmp)
        if len(result) > 0:
            return Result(True, message='No match found, please select from similarly spelt items using item ID or try again (SD)', obj=result)
    result = item_leven_search(query)
    if len(result) > 0:
        ids = []
        for res in result:
            ids.append(res[0])
        result = get_item_by_id(ids)
        return Result(True, message='No match found, please select from similarly spelt items using item ID or try again (LD)', obj=result)
    return Result(False, message='No item found check spelling or use item number')

def get_enchant_lvl(lvl):
    enchant = False
    ench_lvl = 0
    lvl = lvl.lower()
    if re.search("[+][0-9]+", lvl):
        ench_lvl = int(lvl[1:])
        if ench_lvl <= 21:
            enchant = True
    else:
        try:
            ench_lvl = 16 + ['i', 'ii', 'iii', 'iv', 'v'].index(lvl)
        except ValueError as e:
            pass
        else:
            enchant = True
    return Result(enchant, code=ench_lvl)


def format_item_info(item: ItemInfo):
    levels = ['I', 'II', 'III', 'IV', 'V']
    if item.elvl == 0:
        level = ''
    elif item.elvl <= 15:
        level = f'+{str(item.elvl)}'
    else:
        level = levels[item.elvl-16]
    embed = discord.Embed(title=f'{level} {item.item_name.strip()}', url=item.item_url, description=item.item_desc)
    embed.set_author(name='BDO Item Info', icon_url='https://cdn.discordapp.com/app-icons/754046514573344788/1685046eb02a2bd9c62df89c4849d765.png')
    embed.set_thumbnail(url=item.item_icon)
    embed.add_field(name='Item ID', value=f'{item.item_id}')
    embed.add_field(name='Item Type', value=f'{item.item_type}')
    # message = f'{item.item_url}\n```{level}{item.item_name.strip()}\nID: {item.item_id}\n'
    # message = f'{message}Item Type: {item.item_type}\n'
    if item.item_sockets > 0:
        embed.add_field(name='Crystal Slots', value=f'{item.item_sockets}')
        # message = f'{message}Crystal Slots: {item.item_sockets}\n'
    if item.elvl_info:
        message = '' #f'{message}Item Stats:\n'
        if item.elvl_info['damage'] != 0:
            message = f'{message}AP: {item.elvl_info["damage"]}\n'
        if item.elvl_info['defense'] != 0:
            message = f'{message}DP: {item.elvl_info["defense"]}\n'
        if item.elvl_info['accuracy'] != 0:
            message = f'{message}Accuracy: {item.elvl_info["accuracy"]}\n'
        if item.elvl_info['evasion'] != 0:
            message = f'{message}Evasion: {item.elvl_info["evasion"]}\n'
        if item.elvl_info['dreduction'] != 0:
            message = f'{message}Damage Reduction: {item.elvl_info["dreduction"]}\n'
        # message = f'{message}_________________________________________\n'
        if item.elvl_info['edescription'] != 0:
            markup = item.elvl_info['edescription']
            soup = BeautifulSoup(markup, 'html.parser')
            for text in soup.stripped_strings:
                message = f'{message}{text}\n'
        embed.add_field(name='Item Stats', value=message, inline=False)
        # message = f'{message}_________________________________________\n'
        if item.elvl_info.get('need_enchant_item_name', 0) != 0:
            message = ''
            message = f'{message}Enchancement:\n{item.elvl_info["need_enchant_item_name"]}\n'
        if item.elvl_info.get('enchant_chance', 0) != 0:
            message = f'{message}Base Enchance Chance: {item.elvl_info["enchant_chance"]}\n'
            embed.add_field(name='Enhancement', value=message, inline=False)
    embed.add_field(name='Marketplace Info', value='Loading Marketplace Information...', inline=False)
    # message = f'{message}{item.item_desc}\n'
    return embed

def format_mp_info(item_info, embed):
    item = item_info.obj
    message = ''
    if item_info.status:
        if item_info.message:
            message = f'{message}{item_info.message}\n'
        message = f'{message}Item Price: {locale.currency(item.mp_price, grouping=True)}\n'
        message = f'{message}Market Place Quantity: {item.mp_count}'
        
    else:
        message = f'{message}{item_info.message}'
    embed.set_field_at(index=len(embed.fields)-1, name='Current Marketplace Data', value=message, inline=False)
    return embed

# https://www.sqlite.org/spellfix1.html sqlite Levenshtein
# https://pypi.org/project/Metaphone/ python double metaphone
# https://github.com/maxbachmann/rapidfuzz python levenshtein
# https://www.postgresql.org/docs/13/fuzzystrmatch.html#id-1.11.7.24.7 postgres fuzzy matching
# https://www.sqlitetutorial.net/sqlite-index/ sqlite index
# https://database.desertcore.com/download/ bdo item database
# https://omegapepega.com/na/6214/0 bdo marketplace api
# https://github.com/kookehs/bdo-marketplace bdo marketplace website phaser
# https://grasswiki.osgeo.org/wiki/Build_SQLite_extension_on_Linux this was painfully obviously
# replace to '' = ['(', ')', '-', "'", ':', '[', ']']
# replace to ' ' = '  ', '/'
# remove leading / trailing spaces
