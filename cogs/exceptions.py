from discord.ext import commands


class FailAdminCheck(commands.CheckFailure):
    pass

class FailGearChannelCheck(commands.CheckFailure):
    pass