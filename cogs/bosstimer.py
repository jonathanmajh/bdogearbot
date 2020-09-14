# GARMOTH_SCHEDULE = [[2, 3, 0], [4, 3, 0], [6, 23, 45]]
# wday, hour, minute in UTC 15 min early

# @tasks.loop(seconds=60.0)
# async def boss_nagging():
#     time_now = time.gmtime()
#     for spawn in GARMOTH_SCHEDULE:
#         if time_now.tm_wday == spawn[0]:
#             if time_now.tm_hour == spawn[1]:
#                 if time_now.tm_min == spawn[2]:
#                     channel = bot.get_channel(715760182201679883)
#                     message = '<@!150050397883596800> Garmoth in 15 minutes CTG when?????'
#                     await channel.send(message)