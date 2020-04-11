import discord
from discord.ext import commands

from core import utils
from cogs import errors

from config.config import config
from config.messages import Messages as messages
from config.emotes import Emotes as emote

class Warden (commands.Cog):
    """A cog for database lookups"""

    def __init__ (self, bot):
        self.bot = bot
        self.errors = errors.Errors(bot)

    @commands.command()
    @commands.is_owner()
    async def leaveAllGuilds (self, ctx: commands.Context):
    	"""Leave all guilds"""
    	guilds = self.bot.guilds
    	if guilds is not None and len(guilds) > 0:
	    	for g in guilds:
	    		print(g.name)
	    		if g.id != config.guild_id and \
	    		   g.id != 637724748960235540: # wormhole
	    			await g.leave()
	    			await ctx.send("Left {} (id {})".format(g.name, g.id))
	    			return
	    		else:
	    			await ctx.send("Staying in {}".format(g.name))
    	await ctx.send(f":ok_hand:")

def setup(bot):
    bot.add_cog(Warden(bot))
