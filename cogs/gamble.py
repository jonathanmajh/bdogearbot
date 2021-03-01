from discord.ext import commands, tasks
from bin.database import get_item_price, save_item_price, get_item_by_id
import time
from datetime import timedelta, datetime
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import requests
import math

ACCESSORY_IDS = [
    11607,  # Ogre
    11625,  # Sicil
    11628,  # Serap
    11629,  # Tung Neck
    11630,  # Laytenn
    11653,  # Debore
    11726,  # Ruby
    11727,  # Sapphire
    11728,  # Topaz
    11729,  # Emerald
    11730,  # Diamond
    11828,  # Tung Ear
    11834,  # Narc
    11853,  # Disto
    11855,  # Dawn
    11856,  # Ethereal
    11926,  # Manos Ruby Earring
    11927,  # Manos Sapphire Earring
    11928,  # Manos Topaz Earring
    12031,  # Crescent
    12032,  # Cadry
    12042,  # Ronaros
    12060,  # EyeRuin
    12061,  # TungRing
    12068,  # OminousRing
    12126,  # Manos Ruby Ring
    12128,  # Manos Topaz Ring
    12229,  # Centaurus Belt
    12230,  # Basilisk's Belt
    12236,  # Valtarra Eclipsed Belt
    12237,  # Tungrad Belt
    12251,  # Orkinrad
    12257,  # turo
    12326,  # Manos Red Coral Belt
    12327,  # Manos Blue Coral Belt
    12328,  # Manos Green Coral Belt
    12329,  # Manos Golden Coral Belt
    12330,  # Manos White Coral Belt
    # 705509,  # Manos Necklace
    # 705510,  # Manos Earring
    # 705511,  # Manos Ring
    # 705512,  # Manos Belt
]


def refresh_data():
    time_now = datetime.now()
    prices = []
    for item in ACCESSORY_IDS:
        price = get_item_price(item)
        if not price[0] or (datetime.strptime(price[7], '%Y-%m-%d %H:%M:%S.%f') + timedelta(minutes=60) < time_now):
            price = update_item_price(item)
            if not price[0]:
                continue
            save_item_price(price)
        prices.append(price)
    return prices


def update_item_price(item):
    URL = f'https://na-trade.naeu.playblackdesert.com/Trademarket/GetWorldMarketSubList'
    r = requests.post(URL, headers={'Content-Type': 'application/json',
                                    'User-Agent': 'BlackDesert'}, data="{'keyType' : 0, 'mainKey': "+str(item)+"}")
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
    else:
        return [False]


LEVELS = {
    'base': 1,
    'pri': 2,
    'duo': 3,
    'tri': 4,
    'tet': 5,
    'pen': 6,
}


def check_level(level):
    if level.lower() in LEVELS:
        return LEVELS[level]
    else:
        return False


CHANCES = [1, 0.7, 0.5, 0.405, 0.3, 0.105]
STACKS = [0, 18, 40, 44, 110, 200]

def calc_probability(start, end):
    chance = 1
    for tap in CHANCES[start: end]:
        chance = chance * tap
    return chance


millnames = ['', ' K', ' M', ' B', ' T']


def millify(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


class GambleCog(commands.Cog, name='EnchancementGambling'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gamble')
    async def gamble_accessory(self, ctx, start='base', end='tri', calc='%'):
        start = check_level(start)
        end = check_level(end)
        if start and end:
            if calc == '%' or calc == '$':
                await ctx.send('```Getting Market Prices for Accessories Please Wait\nChance to One Tap from {} to {}: {:.2%}```'.format(ctx.args[2].upper(), ctx.args[3].upper(), calc_probability(start, end)))
                item_prices = refresh_data()
                db = TinyDB(storage=MemoryStorage)
                table = db.table(str(datetime.now()))
                item_ids = []
                for item in item_prices:
                    cost = item[start] + (item[1] * (end - start))
                    revenue = item[end] * 0.845
                    if calc == '%':
                        profit = revenue/cost
                    else:
                        profit = revenue-cost
                    table.insert({'item_id': item[0], 'profit': profit})
                    item_ids.append(item[0])
                sort = sorted(table.all(), key=lambda k: k['profit'])
                sort.reverse()
                sort[:20]
                item_names = dict(get_item_by_id(item_ids))
                msg = '```|  Profit |    Name'
                for thing in sort[0:20]:
                    if calc == '%':
                        profit_str = '{:.0%}'.format(thing['profit'])
                        msg = f'{msg}\n|  {profit_str.rjust(6)} | {item_names[thing["item_id"]]}'
                    else:
                        msg = f'{msg}\n| ${millify(thing["profit"]).rjust(6)} | {item_names[thing["item_id"]]}'
                msg = f'{msg}```'
                await ctx.send(msg)
            else:
                await ctx.send('Invalid profit type, please use "%" or "$"')
        else:
            await ctx.send('Invalid enhancement levels use: base, pri, duo, tri, tet, pen')


def setup(bot):
    bot.add_cog(GambleCog(bot))
