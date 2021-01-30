from discord.ext import commands, tasks
from bin.database import get_item_price, save_item_price, get_item_by_id
import time
from datetime import timedelta, datetime
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import requests
import math

ACCESSORY_IDS = [
    11607, # Ogre
    11625, # Sicil
    11628, # Serap
    11629, # Tung Neck
    11630, #Laytenn
    11653, # Debore
    11726, #Ruby
    11727, #Sapphire
    11728, # Topaz
    11729, #Emerald
    11730, #Diamond
    11828, #Tung Ear
    11834, #Narc
    11853, #Disto
    11855, #Dawn
    11856, #Ethereal
    11926, #Manos Ruby Earring
    11927,# Manos Sapphire Earring
    11928, #Manos Topaz Earring	
    12031, #Crescent
    12032, #Cadry
    12042, #Ronaros
    12060, #EyeRuin
    12061, #TungRing
    12068, #OminousRing
    12126,#Manos Ruby Ring	
    12128,#Manos Topaz Ring	
    12229,#Centaurus Belt
    12230,#Basilisk's Belt
    12236,#Valtarra Eclipsed Belt
    12237,#Tungrad Belt	
    12251, #Orkinrad
    12257, #turo
    12326,#Manos Red Coral Belt
    12327,#Manos Blue Coral Belt
    12328,#Manos Green Coral Belt
    12329,#Manos Golden Coral Belt	
    12330,#Manos White Coral Belt
    705509,#Manos Necklace
    705510,#Manos Earring
    705511,#Manos Ring
    705512,#Manos Belt
]

def refresh_data():
    time_now = datetime.now()
    prices = []
    for item in ACCESSORY_IDS:
        price = get_item_price(item)
        if not price[0] or (datetime.strptime(price[7], '%Y-%m-%d %H:%M:%S.%f') + timedelta(minutes=60) < time_now):
            price = update_item_price(item)
            if not price[0]:
                next
            save_item_price(price)
        prices.append(price)
    return prices

def update_item_price(item):
    URL = f'https://marketweb-na.blackdesertonline.com/Trademarket/GetWorldMarketSubList'
    r = requests.post(URL, headers={'Content-Type':'application/json', 'User-Agent':'BlackDesert'}, data="{'keyType' : 0, 'mainKey': "+str(item)+"}")
    if r.status_code == 200:
        try:
            response = r.json()['resultMsg']
            response = response.split("|")
            result = []
            result.append(item)
            for line in response:
                level = line.split('-')
                if len(level) > 3:
                    result.append(int(level[3]))
            result.append(datetime.now())
            return result
        except Exception as e:
            return [False]
        print(response)
    else:
        return [False]

def check_level(level):
    LEVELS = {
        'base': 1,
        'pri': 2,
        'duo': 3,
        'tri': 4,
        'tet': 5,
        'pen': 6,
    }

    if level.lower() in LEVELS:
        return LEVELS[level]
    else:
        return False

millnames = ['',' K',' M',' B',' T']

def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

class GambleCog(commands.Cog, name='EnchancementGambling'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gamble')
    async def gamble_accessory(self, ctx, start='base', end='tri', calc='%'):
        start = check_level(start)
        end = check_level(end)
        if start and end:
            if calc=='%' or calc=='$':
                item_prices = refresh_data()
                db = TinyDB(storage=MemoryStorage)
                table = db.table(str(datetime.now()))
                item_ids = []
                for item in item_prices:
                    print(item)
                    if calc=='%':
                        profit = item[end]/item[start]
                    else:
                        profit = item[end]-item[start]
                    table.insert({'item_id':item[0], 'profit':profit})
                    item_ids.append(item[0])
                sort = sorted(table.all(), key=lambda k: k['profit'])
                sort.reverse()
                sort[:20]
                item_names = dict(get_item_by_id(item_ids))
                msg = '```| Profit |    Name'
                for thing in sort[0:20]:
                    if calc=='%':
                        msg = '{}\n| {:.0%}  | {}'.format(msg, thing['profit'], item_names[thing['item_id']])
                    else:
                        msg = '{}\n| $ {} | {}'.format(msg, millify(thing['profit']), item_names[thing['item_id']])
                msg = f'{msg}```'
                await ctx.send(msg)
            else:
                await ctx.send('Invalid profit type, please use "%" or "$"')
        else:
            await ctx.send('Invalid enhancement levels use: base, pri, duo, tri, tet, pen')

def setup(bot):
    bot.add_cog(GambleCog(bot))