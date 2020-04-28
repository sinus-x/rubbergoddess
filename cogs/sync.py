import discord
from discord.ext import commands

from core.config import config
from core.text import text
from core import check, rubbercog

class Sync(rubbercog.Rubbercog):
    """Maste-Slave server synchronization"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False
    	#TODO Only act on master guild

    @commands.check(check.is_mod)
    @commands.command()
    async def sync(self, ctx: commands.Context):
    	"""Sync all permissions with slave"""
    	await self.throwNotification(ctx, text.get("error", "not implemented"))
    	return

    async def on_member_update(self, before: discord.Member, after: discord.Member):
    	"""Sync user permission changes"""
    	return

    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
    	"""Sync role changes"""
    	return

    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
    	"""Sync bans"""
    	return


def setup(bot):
    bot.add_cog(Sync(bot))
