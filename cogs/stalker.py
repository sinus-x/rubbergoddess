from sqlalchemy.orm.exc import NoResultFound

import discord
from discord.ext import commands

import utils
from cogs import room_check
from features import verification
from repository.database import database, session
from repository.database.verification import User

from config.config import Config as config
from config.messages import Messages as messages
from config.emotes import Emotes as emote

class Stalker (commands.Cog):
	def __init__ (self, bot):
		self.bot = bot
		self.check = room_check.RoomCheck(bot)

	async def is_admin (ctx):
		return ctx.author.id == config.admin_id

	async def is_mod (ctx):
		guild = ctx.message.guild
		mod = discord.utils.get(guild.roles, name="MOD")
		return mod in ctx.author.roles

	async def is_in_modroom (ctx):
		return ctx.message.channel.id == config.mod_room


	@commands.check(is_mod)
	@commands.check(is_in_modroom)
	@commands.command()
	async def whois (self, ctx, discord_id: str):
		guild = ctx.message.guild
		try:
			user = session.query(User).filter(
				User.discord_id == discord_id).one()
			account = discord.utils.get(
				guild.members, id=int(discord_id))
		except NoResultFound:
			user = None
			account = None

		description = "{} ({})".format(account.mention, discord_id) \
			if account else discord_id

		embed = discord.Embed(color=config.color,
			title="?whois",
			description=description)
		if not account:
			embed.add_field(inline=False, name="User not found", value=discord_id)
		if user and account:
			if account.name == account.display_name:
				name = "**{}**".format(account.name)
			else:
				name = "**{}** ({})".format(account.name, account.display_name)
			embed.add_field(inline=True, name="Username", value=account.name)
			embed.add_field(inline=True, name="Login", value=user.login)
			embed.add_field(inline=True,
				name="Verification code", value="`{}`".format(user.code))
			embed.add_field(inline=True, name="Group", value=user.group)
			embed.add_field(inline=True, name="Status", value=user.status)
			embed.add_field(inline=True,
				name="Last change", value=user.changed)
			if user.comment and len(user.comment) > 0:
				embed.add_field(inline=False,
					name="Comment", value=user.comment)
		embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
		await ctx.send(embed=embed)
		try:
			await ctx.message.delete()
		except discord.HTTPException:
			return

	@whois.error
	async def whoisHelp (self, ctx, error):
		embed = discord.Embed(color=config.color,
			title="?whois",
			description="Entered command is not valid")
		embed.add_field(name="Usage:", value="?whois <int: user>")
		embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
		await ctx.send(embed=embed)

	@commands.check(is_mod)
	@commands.check(is_in_modroom)
	@commands.command()
	async def delete (self, ctx, discord_id: str):
		
		return

	@delete.error
	async def deleteHelp (self, ctx, error):
		embed = discord.Embed(color=config.color,
			title="?delete",
			description="Entered command is not valid")
		embed.add_field(name="Usage:", value="?delete <int: discord_id>")
		embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
		await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Stalker(bot))
