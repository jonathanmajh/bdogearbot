import re

from database import item_no_phone, item_exact_search, item_like_search, item_phone_search, item_leven_search, get_item_by_id
from models import Result

from metaphone.metaphone import doublemetaphone


def combo_search(query: str):
    """search for user's query"""
    query = query.replace("(", "").replace(")", "").replace("-", "").replace("'",
            "").replace(":", "").replace("[", "").replace("]", "").replace("/", " ").replace("  ", " ")
    result = item_exact_search(query)
    if len(result) > 0:
        return Result(True, message='Multiple matches found, please select using item ID', obj=result)
    result = item_like_search(query)
    if len(result) > 0:
        return Result(True, message='Multiple matches found, please select using item ID', obj=result)
    result = item_phone_search(doublemetaphone(query))
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
    if re.search("[+][0-9]+", lvl):
        ench_lvl = lvl[1:]
        if ench_lvl <= 21:
            enchant = True
    try:
        ench_lvl = 16 + ['i', 'ii', 'iii', 'iv', 'v'].index(lvl)
    except ValueError as e:
        pass
    else:
        enchant = True
    return Result(enchant, code=ench_lvl)
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
