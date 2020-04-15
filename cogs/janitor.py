import discord
from discord.ext import commands

from core import rubbercog
from config.config import config
from config.messages import Messages as messages

class Janitor(rubbercog.Rubbercog):
    """Manage channels"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def purge(self, ctx: commands.Context, channel: discord.TextChannel = None, *params):
        """Delete messages from channel

        channel: A text channel
        limit: Optional. How many messages to delete. If not present, delete all
        users: Optional. Only selected user IDs.
        pins: Optional. How to treat pinned posts. 'skip' (default), 'stop', 'ignore'
        """
        await self.throwNotification(ctx, messages.err_not_implemented)
        return

        if channel is None:
            await self.throwHelp(ctx)
            return

        # get parameters
        #FIXME Can this be done in a cleaner way? 
        limit = None
        pins = "skip"
        users = None
        for param in params:
            if param.startswith("limit="):
                try:
                    limit = int(param.replace("limit=",""))
                except ValueError:
                    self.throwHelp(ctx)
                    return
            elif param.startswith("pins="):
                if value.replace("pins=", "") in ["stop", "ignore"]:
                    pins = value.replace("pins=","")
                else:
                    self.throwHelp(ctx)
                    return
            elif param.startswith("users="):
                try:
                    users = [int(x) for x in param.replace("users=","").split(",")]
                except ValueError:
                    self.throwHelp(ctx)
                    return

        #TODO Decide what to do depending on pins|users state
        #     On pinStop, we have to go message-by-message, otherwise the
        #     .purge() can be used.

        #TODO generate report

def setup(bot):
    bot.add_cog(Janitor(bot))