import discord
from discord.ext import commands

from core import config, emote, check, rubbercog, utils

class Warden (rubbercog.Rubbercog):
    """A cog for database lookups"""
    def __init__ (self, bot):
        super().__init__(bot)
        self.visible = False

    @commands.command()
    @commands.check(check.is_bot_owner)
    async def leaveAllGuilds (self, ctx: commands.Context):
    	"""Leave all guilds"""
    	guilds = self.bot.guilds
    	if guilds is not None and len(guilds) > 0:
	    	for g in guilds:
	    		if g.id != config.guild_id and \
	    		   g.id != 637724748960235540: # wormhole
	    			await g.leave()
	    			await ctx.send("Left **{}** (id {})".format(g.name, g.id))
	    			return
	    		else:
	    			await ctx.send("Staying in **{}**".format(g.name))
    	await ctx.send(f":ok_hand:")

def setup(bot):
    bot.add_cog(Warden(bot))
