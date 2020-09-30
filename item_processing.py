import re
from bs4 import BeautifulSoup

import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

from database import item_no_phone, item_exact_search, item_like_search, item_phone_search, item_leven_search, get_item_by_id
from models import Result, ItemInfo

from metaphone.metaphone import doublemetaphone


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
    levels = ['I ', 'II ', 'III ', 'IV ', 'V ']
    if item.elvl == 0:
        level = ''
    elif item.elvl <= 15:
        level = f'+{str(item.elvl)} '
    else:
        level = levels[item.elvl-16]
    message = f'```{level}{item.item_name.strip()}\nID: {item.item_id}\n'
    message = f'{message}Item Type: {item.item_type}\n'
    if item.item_sockets > 0:
        message = f'{message}Crystal Slots: {item.item_sockets}\n'
    message = f'{message}Item Stats:\n'
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
    message = f'{message}_________________________________________\n'
    if item.elvl_info['edescription'] != 0:
        markup = item.elvl_info['edescription']
        soup = BeautifulSoup(markup, 'html.parser')
        for text in soup.stripped_strings:
            message = f'{message}{text}\n'
    message = f'{message}_________________________________________\n'
    if item.elvl_info.get('need_enchant_item_name', 0) != 0:
        message = f'{message}Enchancement:\n{item.elvl_info["need_enchant_item_name"]}\n'
    if item.elvl_info.get('enchant_chance', 0) != 0:
        message = f'{message}Base Enchance Chance: {item.elvl_info["enchant_chance"]}\n'
    message = f'{message}{item.item_desc}\n'
    return message

def format_mp_info(item_info):
    # levels = ['I ', 'II ', 'III ', 'IV ', 'V ']
    item = item_info.obj
    # if item.elvl == 0:
    #     level = ''
    # elif item.elvl <= 15:
    #     level = f'+{str(item.elvl)} '
    # else:
    #     level = levels[item.elvl-16]
    # message = f'```{level}{item.item_name.strip()}\nID: {item.item_id}\n'
    message = 'Market Place Information:\n'
    if item_info.status:
        if item_info.message:
            message = f'{message}{item_info.message}\n'
        message = f'{message}Item Price: {locale.currency(item.mp_price, grouping=True)}\n'
        message = f'{message}Market Place Quantity: {item.mp_count}'
        
    else:
        message = f'{message}{item_info.message}'
    return f'{message}```'

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
