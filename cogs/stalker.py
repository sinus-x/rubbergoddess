from sqlalchemy.orm.exc import NoResultFound

import discord
from discord.ext import commands

import utils
from cogs import errors
from features import verification
from repository import user_repo
from repository.database import database, session
from repository.database.verification import User

from config.config import Config as config
from config.messages import Messages as messages
from config.emotes import Emotes as emote

repository = user_repo.UserRepository()

class Stalker (commands.Cog):
    """A cog for database lookups"""

    def __init__ (self, bot):
        self.bot = bot
        self.errors = errors.Errors(bot)

    async def is_in_modroom (ctx):
        return ctx.message.channel.id == config.mod_room

    def dbobj2email (self, dbobj):
        if dbobj is not None:
            if dbobj.group == "FEKT":
                email = dbobj.login + "@stud.feec.vutbr.cz" \
                if "@" not in dbobj.login else dbobj.login
            elif dbobj.group == "VUT":
                email = dbobj.login + "@vutbr.cz" if "@" not in dbobj.login else dbobj.login
            else:
                email = dbobj.login
            return email
        return

    @commands.guild_only()
    @commands.command(name="whois", aliases=["stalk"])
    async def whois (self, ctx: commands.Context, member: discord.Member = None, pin = None):
        """Get information about user

        member: A server member
        pin: A "pin" string that will prevent the embed from disappearing
        """
        if member is None:
            await self.errors._getHelp(ctx)
            return

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        pin = self.errors._parsePin(pin)

        # get user from database
        try:
            dbobj = repository.get_users(discord_id=str(member.id))[0]
        except:
            dbobj = None
        
        t = "📌 " if pin else ""
        t += config.default_prefix + ctx.command.name
        embed = discord.Embed(color=config.color,
            title=t, description=member.mention)
        n = "**{} ({})**".format(member.nick, member.name) \
            if member.nick is not None else "**{}**".format(member.name)
        embed.add_field(name="Discord user data",
            value="{name}\n{d_id}\nMember since {date}".format(
                name=n, d_id=member.id, date=member.joined_at.strftime("%Y-%m-%d")))

        # do not display sensitive information in public channels
        if dbobj is not None and ctx.channel.id == config.mod_room:
            # add embeds
            email = self.dbobj2email(dbobj)
            embed.add_field(name="E-mail", value=email, inline=False)
            embed.add_field(name="Verification code", value=dbobj.code if dbobj.code else "_none_")
            embed.add_field(name="Status", value=dbobj.status)
            embed.add_field(name="Last changed", value=dbobj.changed)
            if dbobj.comment is not None and len(dbobj.comment) > 0:
                embed.add_field(name="Comment", value=dbobj.comment, inline=False)
        elif not dbobj and ctx.channel.id == config.mod_room:
            embed.add_field(name="Not in database", value="Server only", inline=False)
        elif dbobj is not None and ctx.channel.id != config.mod_room:
            embed.add_field(name="Status", value=dbobj.status, inline=False)
            if dbobj.comment is not None and len(dbobj.comment) > 0:
                embed.add_field(name="Comment", value=dbobj.comment, inline=False)

        embed.add_field(inline=False,
            name="Roles", value=', '.join(list((m.name) for m in member.roles[::-1])[:-1]))

        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx, now=True)

    @commands.guild_only()
    @commands.group(aliases=["db"])
    @commands.has_guild_permissions(administrator=True)
    async def database (self, ctx: commands.Context):
        """Manage users"""
        if ctx.invoked_subcommand is None:
            await self.errors._getOptions(ctx)

    @database.command(name="add")
    async def database_add (self, ctx: commands.Context,
                                  member: discord.Member = None,
                                  login: str = None, group: discord.Role = None):
        """Add user to database

        member: A server member
        login: xlogin (FEKT, VUT) or e-mail
        group: A role from `roles_native` or `roles_guest` in config file
        """
        if member is None or login is None or group is None:
            await self.errors._getHelp(ctx)
            return

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        verify = discord.utils.get(guild.roles, name="VERIFY")

        # try to write to database
        try:
            result = repository.get_users(discord_id=str(member.id))[0]
            await self.errors._getError(ctx, messages.stalker_err_new_entry_exists)
            return
        except IndexError:
            # no result is good, we won't have collision
            pass

        try:
            repository.add_user(discord_id=str(member.id), login=login,
                            group=group.name, status="verified", code="MANUAL")
        except:
            await self.errors._getError(ctx, messages.stalker_err_new_entry_write)
            return

        # assign roles, if neccesary
        if verify not in member.roles:
            await member.add_roles(verify)
        if group not in member.roles:
            await member.add_roles(group)

        # display the result
        await self.whois(ctx, member)
        

    @database.command(name="remove", aliases=["delete"])
    async def database_remove (self, ctx: commands.Context,
                                     member: discord.Member = None, force: str = None):
        """Remove user from database

        member: A server member
        force: "force" string. If omitted, show what will be deleted
        """
        if member is None:
            await self.errors._getHelp(ctx)
            return

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        force = self.errors._parseForce(force)

        try:
            if force:
                result = repository.delete_users(discord_id=str(member.id))
            else:
                result = repository.get_users(discord_id=str(member.id))
        except:
            await self.errors._getError(ctx, messages.stalker_err_read)
            return

        #TODO make function for command title
        p = ' '.join((p.name) for p in ctx.command.parents) + " " if ctx.command.parents else ""
        t = config.default_prefix + p + ctx.command.name
        d = "Result" if force else "Simulation, run with `force` to apply"
        if force:
            embed = discord.Embed(color=config.color_success, title=t, description=d)
            # delete
            if result is None or result < 1:
                await self.errors._getError(ctx, messages.stalker_err_delete_not_found)
                return
            embed.add_field(inline=False,
                name="Success", value="Deleted {} entries".format(result))
            #TODO remove all roles
        else:
            # simulate
            embed = discord.Embed(color=config.color_notify, title=t, description=d)
            for r in result:
                embed.add_field(inline=False,
                    name=self.dbobj2email(r),
                    value=discord.utils.get(guild.members, id=int(r.discord_id)).mention)
            if len(result) < 1:
                embed.add_field(name="No entry", value="User is not in the database", inline=False)
        embed.set_footer(text=ctx.author)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx)


    @database.group(name="update")
    async def database_update (self, ctx: commands.Context):
        """Set of functions to update database entries"""
        if ctx.invoked_subcommand is None:
            await self.database_update_help(ctx)

    @database_update.command(name="login")
    async def database_update_login (self, ctx: commands.Context, member: discord.Member, login: str):
        """Update user's registered login

        member: A server member
        login: User's xlogin (FEKT, VUT) or e-mail
        """
        await self.errors._getNotification(ctx, messages.exc_not_implemented, pin=False)
        return

    @database_update.command(name="group")
    async def database_update_group (self, ctx: commands.Context, member: discord.Member, group: discord.Role):
        """Update user's registered group

        member: A server member
        group: A role from `roles_native` or `roles_guest` in config file
        """
        await self.errors._getNotification(ctx, messages.exc_not_implemented, pin=False)

    @database_update.command(name="status")
    async def database_update_status (self, ctx: commands.Context, member: discord.Member, status: str):
        """Update user's verification status

        member: A server member
        status: unknown, pending, verified, kicked, banned
        """
        await self.errors._getNotification(ctx, messages.exc_not_implemented, pin=False)

    @database_update.command(name="comment")
    async def database_update_comment (self, ctx: commands.Context, member: discord.Member, *args):
        """Update comment on user

        member: A server member
        args: Commentary on user
        """
        await self.errors._getNotification(ctx, messages.exc_not_implemented, pin=False)

    @database_update.command(name="nickname")
    async def database_update_nickname (self, ctx: commands.Context, member: discord.Member, *args):
        """Update user's nickname

        member: A server member
        args: A new nickname
        """
        await self.errors._getNotification(ctx, messages.exc_not_implemented, pin=False)

    @database_update.command(name="tempnickname")
    async def database_update_nickname (self, ctx: commands.Context, member: discord.Member, *args):
        """Update user's nickname

        member: A server member
        args: A new temporary nickname. If empty, reset to default
        """
        await self.errors._getNotification(ctx, messages.exc_not_implemented, pin=False)

    @database.command(name="statistics", aliases=["stats"])
    async def database_statistics (self, ctx: commands.Context):
        """Display statistics about known users"""
        await self.errors._getNotification(ctx, messages.exc_not_implemented, pin=False)

    @database.command(name="today")
    async def database_today (self, ctx: commands.Context):
        """Display the count of users that joined/were verified today"""
        await self.errors._getNotification(ctx, messages.exc_not_implemented, pin=False)


def setup(bot):
    bot.add_cog(Stalker(bot))
