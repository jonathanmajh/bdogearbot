# simple error handling adapted from https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
"""
If you are not using this inside a cog, add the event decorator e.g:
@bot.event
async def on_command_error(ctx, error)
For a list of exceptions:
https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exceptions
"""
import discord
import traceback
import sys
from discord.ext import commands
from cogs.exceptions import FailGearChannelCheck, FailAdminCheck

class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def send_pm(self, error):
        user = await self.bot.fetch_user(152611107633233920)
        error = traceback.format_exception(type(error), error, error.__traceback__)
        await user.send('```{}```'.format(error))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            await self.send_pm(error)
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, FailGearChannelCheck):
            await ctx.send(f'{ctx.command} can only be used in gear channel.')

        if isinstance(error, FailAdminCheck):
            await ctx.send(f'{ctx.command} can only be by DiscAdmin.')

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await self.send_pm(error)
            await ctx.send(":scream: Uh Oh! Someone made an oopsie! :sob:\n:poop: Go bug TWICEAhri#4578 to fix it! :rage:")

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))