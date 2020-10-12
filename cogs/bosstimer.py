import time
from datetime import datetime, timedelta

import discord
from bin.models import Result
from discord.ext import commands, tasks


class BossScheduleCog(commands.Cog, name='GarmothSchedule'):
    # TODO swap to use database to store boss spawns
    # use self var to track progression, init to find location after restart
    # different look ahead values depending on boss
    BOSS_SCHEDULE = [
        [0, ['garmoth']],
        [315, ['kzarka', 'nouver']],
        [515, ['kutum', 'karanda']],
        [700, ['karanda']],
        [1000, ['kzarka']],
        [1400, ['kzarka']],
        [1700, ['offin']],
        [2100, ['kutum']],
        [10000, ['nouver']],
        [10315, ['kzarka']],
        [10515, ['karanda']],
        [10700, ['kutum']],
        [11000, ['kzarka']],
        [11400, ['nouver']],
        [11700, ['kutum']],
        [12100, ['nouver']],
        [20000, ['karanda']],
        [20315, ['garmoth']],
        [20515, ['kutum', 'kzarka']],
        [20700, ['karanda']],
        [21400, ['karanda']],
        [21700, ['nouver']],
        [22100, ['kutum', 'offin']],
        [30000, ['vell']],
        [30315, ['karanda', 'kzarka']],
        [30415, ['quint', 'muraka']],
        [30515, ['nouver']],
        [30700, ['kutum']],
        [31000, ['kzarka']],
        [31400, ['kutum']],
        [31700, ['nouver']],
        [32100, ['kzarka']],
        [40000, ['kutum']],
        [40315, ['garmoth']],
        [40515, ['kzarka', 'karanda']],
        [40700, ['nouver']],
        [41000, ['karanda']],
        [41400, ['kutum']],
        [41700, ['karanda']],
        [42100, ['nouver']],
        [50000, ['kzarka']],
        [50315, ['kutum', 'kzarka']],
        [50515, ['karanda']],
        [50700, ['offin']],
        [51000, ['nouver']],
        [51400, ['kutum']],
        [51700, ['nouver']],
        [52100, ['quint', 'muraka']],
        [60000, ['kzarka', 'karanda']],
        [60515, ['nouver', 'kutum']],
        [60700, ['kzarka']],
        [61000, ['kutum']],
        [61400, ['nouver']],
        [61700, ['kzarka']],
        [62100, ['vell']],
    ]

    BOSSES = ['vell', 'garmoth', 'karanda', 'kzarka', 'kutum', 'nouver', 'quint', 'muraka']
    AKA = {'cronmoth': 'Garmoth', 'garmoth': 'Garmoth'} #map of boss alias
    # wday, hour, minute in UTC

    def __init__(self, bot):
        self.bot = bot
        self.boss_nagging.start()
        self.next_boss_i = 0
        self.update_state()

    def update_state(self):
        time_now = time.gmtime()
        time_now = time_now.tm_wday * 10000 + time_now.tm_hour * 100 + time_now.tm_min
        for index, spawn in enumerate(self.BOSS_SCHEDULE):
            if spawn[0] < time_now:
                next
            else:
                self.next_boss_i = index
                break

    def date_compare(self, time_obj: int, early: int = 0):
        """
        If early is specified then its the scheduler checking for warning
        else it is user asking for next boss
        01 June 2020 = monday to use as datum since we only care about the day of the week not day of month
        """
        converted_time = datetime(
            2020, 6, (time_obj//10000)+1, (time_obj%10000)//100, time_obj%100)
        time_now = time.gmtime()
        time_now = datetime(2020, 6, time_now.tm_wday+1,
                            time_now.tm_hour, time_now.tm_min) + timedelta(minutes=early)
        if early:
            time_now = time_now.replace(day=time_now.weekday()+1) # take care of sunday wrap around
            if converted_time < time_now: #event is in the past
                self.update_state()
                return Result(False)
            elif converted_time == time_now:
                self.update_state()
                return Result(True)
            else: #event is in the future
                return Result(False)

        else:
            time_diff = converted_time - time_now
            return Result(True, obj=time_diff)

    @tasks.loop(seconds=60.0)
    async def boss_nagging(self):
        print(f'boss timer {datetime.now()}')
        #garmoth
        if 'garmoth' in self.BOSS_SCHEDULE[self.next_boss_i][1]:
            if self.date_compare(self.BOSS_SCHEDULE[self.next_boss_i][0], 30).status:
                print('sending garmoth spawn message')
                channel = self.bot.get_channel(715760182201679883)
                message = '<@!150050397883596800> Garmoth in 30 minutes CTG when?????'
                await channel.send(message)
        #vell
        elif 'vell' in self.BOSS_SCHEDULE[self.next_boss_i][1]:
            if self.date_compare(self.BOSS_SCHEDULE[self.next_boss_i][0], 45).status:
                print('sending vell spawn message')
                channel = self.bot.get_channel(715760182201679883)
                message = 'Vell in 45 minutes find your nearest **friendly** officer for ride'
                await channel.send(message)
        else:
            if self.date_compare(self.BOSS_SCHEDULE[self.next_boss_i][0], 10).status:
                print('sending normal spawn message')
                channel = self.bot.get_channel(755211391824167012)
                response = f'```Spawning in 10 minutes!!!'
                for boss in self.BOSS_SCHEDULE[self.next_boss_i][1]:
                    response = f'{response}\n{boss}'
                response = f'{response}```'
                await channel.send(response)

    @boss_nagging.before_loop
    async def before_nagging(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    @commands.command(name='nextboss')
    async def next_boss(self, ctx, boss_name: str = None):
        """
        Get ETA to next world boss spawn

        Optional get next spawn for specific world boss

        Bosses: Garmoth, Offin, Vell, Karanda, Kzarka, Muraka, Quint, Nouver
        """
        response = ''
        if boss_name:  # convert to lowercase
            boss_name = boss_name.lower()

        if not boss_name:  # if no name specified find next boss spawn
            time_diff = self.date_compare(self.BOSS_SCHEDULE[self.next_boss_i][0]).obj
            response = f'```Spawning in {int(time_diff.seconds/3600)}h:{int((time_diff.seconds%3600)/60)}m:'
            for boss in self.BOSS_SCHEDULE[self.next_boss_i][1]:
                response = f'{response}\n{boss}'
            response = f'{response}```'
        elif boss_name == 'all':
            response = 'Unimplimented (:'
        elif boss_name == 'muraka':
            response = '```Get Help @:\nCanada: 1-866-531-2600\nUSA:1-800-273-8255```'
        else:
            for i in range(self.next_boss_i, len(self.BOSS_SCHEDULE)):
                if boss_name in self.BOSS_SCHEDULE[i][1]:
                    result = self.date_compare(self.BOSS_SCHEDULE[i][0])
                    if result.status:
                        time_diff = result.obj
                        response = f'Next {boss_name} spawn is in {time_diff.days}d {int(time_diff.seconds/3600)}h:{int((time_diff.seconds%3600)/60)}m'
                        break
        if not response: # try again from the beginning   
            for i in range(len(self.BOSS_SCHEDULE)):
                if boss_name in self.BOSS_SCHEDULE[i][1]:
                    result = self.date_compare(self.BOSS_SCHEDULE[i][0]+70000)
                    if result.status:
                        time_diff = result.obj
                        response = f'Next {boss_name} spawn is in {time_diff.days}d {int(time_diff.seconds/3600)}h:{int((time_diff.seconds%3600)/60)}m'
                        break
        if not response:
            response = f'World boss {boss_name} cannot be found'
        await ctx.send(response)


def setup(bot):
    bot.add_cog(BossScheduleCog(bot))
