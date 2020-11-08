import time
from datetime import datetime, timedelta

import discord
from bin.models import Result
from discord.ext import commands, tasks


class BossScheduleCog(commands.Cog, name='GarmothSchedule'):
    BOSS_SCHEDULE = [
        # Monday
        [100, ['garmoth']],
        [415, ['kzarka', 'nouver']],
        [615, ['kutum', 'karanda']],
        [800, ['karanda']],
        [1100, ['kzarka']],
        [1500, ['kzarka']],
        [1800, ['offin']],
        [2200, ['kutum']],
        # Tuesday
        [10100, ['nouver']],
        [10415, ['kzarka']],
        [10615, ['karanda']],
        [10800, ['kutum']],
        [11100, ['kzarka']],
        [11500, ['nouver']],
        [11800, ['kutum']],
        [12200, ['nouver']],
        # Wed
        [20100, ['karanda']],
        [20415, ['garmoth']],
        [20615, ['kutum', 'kzarka']],
        [20800, ['karanda']],
        [21500, ['karanda']],
        [21800, ['nouver']],
        [22200, ['kutum', 'offin']],
        # Thurs
        [30100, ['vell']],
        [30415, ['karanda', 'kzarka']],
        [30515, ['quint', 'muraka']],
        [30615, ['nouver']],
        [30800, ['kutum']],
        [31100, ['kzarka']],
        [31500, ['kutum']],
        [31800, ['nouver']],
        [32200, ['kzarka']],
        # Fri
        [40100, ['kutum']],
        [40415, ['garmoth']],
        [40615, ['kzarka', 'karanda']],
        [40800, ['nouver']],
        [41100, ['karanda']],
        [41500, ['kutum']],
        [41800, ['karanda']],
        [42200, ['nouver']],
        # Sat
        [50100, ['kzarka']],
        [50415, ['kutum', 'kzarka']],
        [50615, ['karanda']],
        [50800, ['offin']],
        [51100, ['nouver']],
        [51500, ['kutum']],
        [51800, ['nouver']],
        [52200, ['quint', 'muraka']],
        # Sun
        [60100, ['kzarka', 'karanda']],
        [60615, ['nouver', 'kutum']],
        [60800, ['kzarka']],
        [61100, ['kutum']],
        [61500, ['nouver']],
        [61800, ['kzarka']],
        [62200, ['vell']],
    ]

    BOSSES = ['vell', 'garmoth', 'karanda', 'kzarka',
              'kutum', 'nouver', 'quint', 'muraka']
    AKA = {'cronmoth': 'Garmoth', 'garmoth': 'Garmoth'}  # map of boss alias
    # wday, hour, minute in UTC

    def __init__(self, bot):
        self.bot = bot
        self.boss_nagging.start()
        self.next_boss_i = -1
        self.BOSS_WARNING_ROLES = ['10mBossWarning', '30mBossWarning']
        self.update_state()
        
    async def check_roles(self):
        for guild in self.bot.guilds:
            for role in self.BOSS_WARNING_ROLES:
                guild_role = discord.utils.get(guild.roles, name=role)
                if guild_role is None:
                    await guild.create_role(name=role, reason='Missing Boss Warning role in server')


    def update_state(self):
        time_now = time.gmtime()
        time_now = time_now.tm_wday * 10000 + time_now.tm_hour * 100 + time_now.tm_min
        if self.next_boss_i + 1 == len(self.BOSS_SCHEDULE) and self.BOSS_SCHEDULE[-1][0] <= time_now:
            self.next_boss_i = 0
            return True
        if self.next_boss_i == 0 and time_now > 10000:
            return True
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
            2020, 6, (time_obj//10000)+1, (time_obj % 10000)//100, time_obj % 100)
        time_now = time.gmtime()
        time_now = datetime(2020, 6, time_now.tm_wday+1,
                            time_now.tm_hour, time_now.tm_min) + timedelta(minutes=early)
        if early:
            # take care of sunday wrap around
            time_now = time_now.replace(day=time_now.weekday()+1)
            if converted_time < time_now:  # event is in the past
                self.update_state()
                return Result(False)
            elif converted_time == time_now:
                self.update_state()
                return Result(True)
            else:  # event is in the future
                return Result(False)

        else:
            time_diff = converted_time - time_now
            return Result(True, obj=time_diff)

    @tasks.loop(seconds=60.0)
    async def boss_nagging(self):
        print(f'boss timer {datetime.now()}')
        # garmoth
        if 'garmoth' in self.BOSS_SCHEDULE[self.next_boss_i][1]:
            if self.date_compare(self.BOSS_SCHEDULE[self.next_boss_i][0], 30).status:
                channel = self.bot.get_channel(715760181966799010)
                message = '<@!150050397883596800> Garmoth in 30 minutes CTG when?????'
                await channel.send(message)
        # vell
        elif 'vell' in self.BOSS_SCHEDULE[self.next_boss_i][1]:
            if self.date_compare(self.BOSS_SCHEDULE[self.next_boss_i][0], 45).status:
                channel = self.bot.get_channel(715760182201679883)
                message = 'Vell in 45 minutes find your nearest **friendly** officer for ride'
                await channel.send(message)
        if self.date_compare(self.BOSS_SCHEDULE[self.next_boss_i][0], 10).status:
            channel = self.bot.get_channel(755211391824167012)
            response = f'```Spawning in 10 minutes!!!'
            guild_role = discord.utils.get(channel.guild.roles, name=self.BOSS_WARNING_ROLES[0])
            for boss in self.BOSS_SCHEDULE[self.next_boss_i][1]:
                response = f'{response}\n{boss}'
            response = f'{response}``` {guild_role.mention}'
            await channel.send(response)

    @boss_nagging.before_loop
    async def before_nagging(self):
        print('waiting...')
        await self.bot.wait_until_ready()
        await self.check_roles()

    @commands.command(name='bosswarning')
    async def give_boss_warning_role(self, ctx, time: int=10):
        """
        Give role for boss warning, warning can be either 10 or 30 minutes before boss spawns

        Ex: ?bosswarning 10
        """
        guild = ctx.guild
        role_name = f'{str(time)}mBossWarning'
        role = discord.utils.get(guild.roles, name=role_name)
        user = ctx.author
        try:
            await user.add_roles(role, reason='User requested boss warning role')
        except Exception as e:
            await ctx.send("Couldn't give you boss warning role, please check my permissions")
        else:
            await ctx.send(f"You've been assigned: {role_name}")

    @commands.command(name='nobosswarning')
    async def remove_boss_warning_role(self, ctx, time: int=10):
        """
        Remove role for boss warning, warning can be either 10 or 30 minutes before boss spawns

        Ex: ?bosswarning 10
        """
        guild = ctx.guild
        role_name = f'{str(time)}mBossWarning'
        role = discord.utils.get(guild.roles, name=role_name)
        user = ctx.author
        try:
            await user.remove_roles(role, reason='User requested boss warning role removal')
        except Exception as e:
            await ctx.send("Couldn't remove your boss warning role, please check my permissions")
        else:
            await ctx.send(f"You've removed from: {role_name}")


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
            time_diff = self.date_compare(
                self.BOSS_SCHEDULE[self.next_boss_i][0]).obj
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
        if not response:  # try again from the beginning
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
