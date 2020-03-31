from sqlalchemy.orm.exc import NoResultFound

import discord
from discord.ext import commands

import utils
from cogs import room_check
from features import verification
from repository import user_repo
from repository.database import database, session
from repository.database.verification import User

from config.config import Config as config
from config.messages import Messages as messages
from config.emotes import Emotes as emote

repository = user_repo.UserRepository()

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
    async def whois (self, ctx, discord_id: str = 0):
        guild = ctx.message.guild
        # get object from database
        try:
            user = session.query(User).filter(
                User.discord_id == discord_id).one()
        except:
            user = None
        # get object from guild data
        account = discord.utils.get(
            guild.members, id=int(discord_id))

        # nothing found
        if not user and not account:
            await self.whoisHelp(ctx)
            return

        # account for nickname aliases
        description = "{} ({})".format(account.mention, discord_id) \
            if account else discord_id
        embed = discord.Embed(color=config.color,
            title="?whois",
            description=description)
        if not user:
            # database object missing
            embed.add_field(inline=False, name="Not in database", value="Server only")
        else:
            if account:
                name = "**{}**".format(account.name)
            else:
                name = "_Unknown, database only_"
            embed.add_field(inline=True,
                name="Username", value=name)
            embed.add_field(inline=True,
                name="Login", value=user.login)
            embed.add_field(inline=True,
                name="Verification code", value=user.code)
            embed.add_field(inline=True,
                name="Group", value=user.group)
            embed.add_field(inline=True,
                name="Status", value=user.status)
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
    async def whoisError (self, ctx, error):
        await self.whoisHelp(ctx)
        return

    async def whoisHelp (self, ctx):
        embed = discord.Embed(color=config.color,
            title="?whois help",
            description=ctx.message.content)
        embed.add_field(
            name="?whois <int: user>",
            value="**user**: User's Discord ID")
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_mod)
    @commands.check(is_in_modroom)
    @commands.command()
    async def addUser (self, ctx, discord_id: str, login: str, group: str):
        if discord_id is None or len(discord_id) < 1 \
        or login is None or len(login) < 1:
            await self.addUserHelp(ctx)
            return

        repository.add_user(
            discord_id=discord_id,
            login=login,
            group=group,
            status="verified",
            code="MANUAL")

        await self.whois(ctx, discord_id)

    @addUser.error
    async def addUserError (self, ctx, error):
        await self.addUserHelp(ctx)

    async def addUserHelp (self, ctx):
        embed = discord.Embed(color=config.color,
            title="?addUser help",
            description=ctx.message.content)
        embed.add_field(
            name="?addUser <int: discord_id> <str: login> <str: group>",
            value="**discord_id**: Users's Discord ID\n" + \
                  "**login**: Their xlogin or e-mail\n" + \
                  "**group**: Assigned group")
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_mod)
    @commands.check(is_in_modroom)
    @commands.command()
    async def deleteUser (self, ctx, discord_id: str, force = None):
        if discord_id is None or len(discord_id) < 1:
            await self.deleteUserHelp(ctx)
            return
        if force == "force":
            force = True

        guild = ctx.message.guild
        try:
            users = session.query(User).filter(
                User.discord_id == discord_id).all()
        except NoResultFound:
            users = None

        embed = discord.Embed(color=config.color,
            title="?deleteUser result" if force else "?deleteUser preview",
            description="Success" if force else "Use `force` to apply")

        if force:
            # delete
            try:
                count = session.query(User).filter(
                    User.discord_id == discord_id).delete()
                embed.add_field(inline=False,
                    name="Success", value="{} entries deleted".format(count))
            except:
                embed.add_field(inline=False,
                    name="Error", value="Unknown error occured. _Helpful, right?_")
        else:
            # show what will be deleted
            if users:
                for user in users:
                    embed.add_field(
                        name=discord_id,
                        value="**{}**".format(user.login))
                    embed.add_field(
                    	name=user.group,
                    	value=user.code if user.code else "_No code_")
                    status = user.status if user.status else "_No status_"
                    status += " ({})".format(user.changed if user.changed else "_No date_")
                    embed.add_field(
                        name=status,
                        value=user.comment if user.comment else "_No comments_")
            else:
                embed.add_field(inline=False,
                    name="No matches found",
                    value=discord_id if discord_id else "0")
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @deleteUser.error
    async def deleteUserError (self, ctx, error):
        await self.deleteUserHelp(ctx)

    async def deleteUserHelp (self, ctx):
        embed = discord.Embed(color=config.color,
            title="?deleteUser help",
            description=ctx.message.content)
        embed.add_field(
            name="?deleteUser <int: discord_id> [force]",
            value="**discord_id**: Users's Discord ID\n" + \
                  "**force**: Do not simulate, remove from database")
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Stalker(bot))
