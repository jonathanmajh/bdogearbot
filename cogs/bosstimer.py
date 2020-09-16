import discord
import time
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from models import Result


class BossScheduleCog(commands.Cog, name='GarmothSchedule'):
    BOSS_SCHEDULE = {
        'garmoth': [[2, 3, 15], [4, 3, 15], [0, 0, 0]],
        'vell': [[3, 0, 0], [6, 21, 0]],
        'karanda': [[0, 5, 15], [0, 7, 0], [1, 5, 15], [2, 0, 0],
                    [2, 7, 0], [2, 14, 0], [3, 3, 15], [4, 5, 15],
                    [4, 10, 0], [4, 17, 0], [5, 5, 15], [6, 0, 0]],
        'kutum': [[2, 21, 0]],
        'offin': [[2, 21, 0]],
    }
    # wday, hour, minute in UTC 15 min early

    def __init__(self, bot):
        self.bot = bot

    def date_compare(self, time_obj: [int]):
        """
        ...
        """
        converted_time = datetime(
            2000, 1, time_obj[0]+1, time_obj[1], time_obj[2])
        time_now = time.gmtime()
        time_now = datetime(2000, 1, time_now.tm_wday+1,
                            time_now.tm_hour, time_now.tm_min)
        if converted_time < time_now:
            return Result(False)
        else:
            time_diff = converted_time - time_now
            return Result(True, obj=time_diff)

    @tasks.loop(seconds=60.0)
    async def boss_nagging(self):
        time_now = time.gmtime()
        for spawn in self.BOSS_SCHEDULE['garmoth']:
            if time_now.tm_wday == spawn[0]:
                if time_now.tm_hour == spawn[1]:
                    minute = (45 if spawn[2] == 0 else spawn[2])
                    if time_now.tm_min == minute:
                        channel = self.bot.get_channel(715760182201679883)
                        message = '<@!150050397883596800> Garmoth in 15 minutes CTG when?????'
                        await channel.send(message)
                        break

    @commands.command(name='nextboss')
    async def next_boss(self, ctx, boss_name: str = None):
        """
        Get ETA to next world boss spawn

        Optional get next spawn for specific world boss

        Bosses: Garmoth, Offin, Vell, Karanda, Kzarka, Muraka, Quint, Nouver
        """

        if boss_name:  # convert to lowercase
            boss_name = boss_name.lower()
        else:  # if no name specified find next boss spawn
            response = 'Unimplimented (:'
        if boss_name == 'all':
            response = 'Unimplimented (:'
        elif boss_name == 'muraka':
            response = 'Get Help @:\nCanada: 1-866-531-2600\nUSA:1-800-273-8255'
        else:
            for spawn in self.BOSS_SCHEDULE[boss_name]:
                result = self.date_compare(spawn)
                if result.status:
                    time_diff = result.obj
                    response = f'Next {boss_name} spawn is in {time_diff.days}d {int(time_diff.seconds/3600)}h:{int((time_diff.seconds%3600)/60)}m'
                    break
        await ctx.send(response)


def setup(bot):
    bot.add_cog(BossScheduleCog(bot))
