import discord
from discord.ext import commands

from core import check, rubbercog
from config.config import config
from config.messages import Messages as messages

class Creator(rubbercog.Rubbercog):
    """Initiate the server for the next semester"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

    @commands.group(name="config")
    @commands.check(check.is_mod)
    @commands.check(check.is_in_modroom)
    async def init(self, ctx: commands.Context):
        """Initiate the guild for next academic year"""
        if ctx.invoked_subcommand is None:
            self.throwHelp(ctx)
            return

    @init.command(name="reset")
    async def init_reset(self, ctx: commands.Context):
        """Delete channels, force reverification"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        return

    @init.command(name="channels")
    async def init_channels(self, ctx: commands.Context):
        """Add subject channels"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        return

    @init.command(name="subjects")
    async def init_subjects(self, ctx: commands.Context):
        """Send react-to-role messages to #add-subjects"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        return



	"""
	?init
	- group

	?init reset
	- delete all channels
	- switch FEKT/VUT roles to REVERIFY

	?init channels
	- load departments
	 - add subjects with their names as descriptions
	   - Should subjects with different shortcuts but same names be merged?

	?init subjects
	- department header (image, pinned)
	- react-to-role subjects
	"""

def setup(bot):
    bot.add_cog(Creator(bot))
