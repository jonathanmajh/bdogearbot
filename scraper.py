import requests
from bs4 import BeautifulSoup
import re
import json
from models import ItemInfo, Result


def get_mp_info(item_info):
    MP_URL = f'https://omegapepega.com/na/{item_info.item_id}/0'
    mp_stats = requests.get(MP_URL)
    message = None
    if mp_stats.status_code == 200:
        if item_info.elvl:
            MP_URL = f'https://omegapepega.com/na/{item_info.item_id}/{item_info.elvl}'
            enchant_mp_stats = requests.get(MP_URL)
            if enchant_mp_stats.status_code == 200:
                mp_stats = enchant_mp_stats
            else:
                message = f'Prices not available for enhancement level {item_info.elvl}, possibly because it falls under a range Ex: +6-+9, the base price is shown below'
        mp_stats = mp_stats.json()
        item_info.mp_count = mp_stats['count']
        item_info.mp_price = mp_stats['pricePerOne']
        return Result(True, message=message, obj=item_info)
    else:
        message = 'This item is not sold on the marketplace'
        return Result(False, message=message, obj=item_info)
    # not available on mp


def get_item_info(item_id, elvl):
    URL = f"https://bdocodex.com/us/item/{item_id}/"
    page = requests.get(URL)
    if page.status_code != 200:
        return Result(False, 'This item cannot be found')
    soup = BeautifulSoup(page.content, 'html.parser')

    item_stats = soup.find('table', 'smallertext')
    try:
        enchantment_info = json.loads(
            item_stats.find(id='enchantment_array').next)
    except AttributeError:
        enchantment_info = None
    else:
        try:
            enchantment_info = enchantment_info[str(elvl)]
        except KeyError:
            enchantment_info = enchantment_info['0']
        
    # access enchantment level as a string not int...

    item_desc = soup.find('hr', 'tooltiphr').parent
    item_type = item_stats.find('span', 'category_text').get_text()
    item_name = soup.find(id='item_name').text 
    icon_url = f'https://bdocodex.com{soup.find("img", "item_icon").attrs["src"]}'
    item_tooltip = ''
    i = 0
    # desc = item_desc.contents
    desc = [text for text in item_desc.stripped_strings]
    while i < len(desc):
        if 'Exclusive:' == desc[i][:10]:
            item_tooltip = f'{item_tooltip}{desc[i]}\n'
        elif desc[i] == '– Description:':
            item_tooltip = f'{item_tooltip}{desc[i+1]}\n' 
        i = i + 1
    # descs = [text for text in item_desc.stripped_strings]
    # for text in item_desc.stripped_strings:
    #     item_tooltip = item_tooltip + text

# description = item_desc.contents[item_desc.contents.index('\r\n– Description:')+2]
    sockets = len(item_desc.find_all('span', 'stone_socket'))
    item = ItemInfo(item_id=item_id, item_url=URL, elvl=elvl, elvl_info=enchantment_info, item_icon=icon_url,
                    item_type=item_type, item_desc=item_tooltip, item_sockets=sockets, item_name=item_name)
    return Result(True, obj=item)
# exclusive = item_desc.find(string=re.compile('Exclusive*'))
# html_info = soup.find()
