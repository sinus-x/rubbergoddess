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
    """A cog for database lookups"""

    def __init__ (self, bot):
        self.bot = bot
        self.check = room_check.RoomCheck(bot)

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

    @commands.command(name="whois", aliases=["stalk"])
    @commands.has_permissions(administrator=True)
    async def whois (self, ctx: commands.Context, member: discord.Member = None, pin = None):
        """Get information about user

        member: A server member
        pin: A "pin" string that will prevent the embed from disappearing
        """
        if member is None:
            await self._getHelp(ctx)
            return

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        pin = self._parsePin(pin)

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


    @commands.group(aliases=["db"])
    @commands.has_permissions(administrator=True)
    async def database (self, ctx: commands.Context):
        """Manage users"""
        if ctx.invoked_subcommand is None:
            await self._getOptions(ctx)

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
            await self._getHelp(ctx)
            return

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        verify = discord.utils.get(guild.roles, name="VERIFY")

        # try to write to database
        try:
            result = repository.get_users(discord_id=str(member.id))[0]
            await self._getError(ctx, messages.stalker_err_new_entry_exists)
            return
        except IndexError:
            # no result is good, we won't have collision
            pass

        try:
            repository.add_user(discord_id=str(member.id), login=login,
                            group=group.name, status="verified", code="MANUAL")
        except:
            await self._getError(ctx, messages.stalker_err_new_entry_write)
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
            await self._getHelp(ctx)
            return

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        force = self._parseForce(force)

        #TODO make function for command title
        p = ' '.join((p.name) for p in ctx.command.parents) + " " if ctx.command.parents else ""
        t = config.default_prefix + p + ctx.command.name
        d = "Result" if force else "Simulation, run with `force` to apply"
        embed = discord.Embed(color=config.color_true, title=t, description=d)
        try:
            if force:
                result = repository.delete_users(discord_id=str(member.id))
            else:
                result = repository.get_users(discord_id=str(member.id))
        except:
            await self._getError(ctx, messages.stalker_err_read)
            return

        if force:
            # delete
            if result is None or result < 1:
                await self._getError(ctx, messages.stalker_err_delete_not_found)
                return
            embed.add_field(inline=False,
                name="Success", value="Deleted {} entries".format(result))
            #TODO remove all roles
        else:
            # simulate
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
        """Manages updating the database"""
        if ctx.invoked_subcommand is None:
            await self.database_update_help(ctx)

    @database_update.command(name="help")
    async def database_update_help(self, ctx: commands.Context):
        """Display help"""
        await self._getHelp(ctx)

    @database_update.command(name="login")
    async def database_update_login (self, ctx: commands.Context, member: discord.Member, login: str):
        """Update user's registered login

        member: A server member
        login: User's xlogin (FEKT, VUT) or e-mail
        """
        await self._getError(ctx, messages.stalker_err_not_implemented, pin=False)
        return

    @database_update.command(name="group")
    async def database_update_group (self, ctx: commands.Context, member: discord.Member, group: discord.Role):
        """Update user's registered group

        member: A server member
        group: A role from `roles_native` or `roles_guest` in config file
        """
        await self._getError(ctx, messages.stalker_err_not_implemented, pin=False)

    @database_update.command(name="status")
    async def database_update_status (self, ctx: commands.Context, member: discord.Member, status: str):
        """Update user's verification status

        member: A server member
        status: unknown, pending, verified, kicked, banned
        """
        await self._getError(ctx, messages.stalker_err_not_implemented, pin=False)

    @database_update.command(name="comment")
    async def database_update_comment (self, ctx: commands.Context, member: discord.Member, *args):
        """Update comment on user

        member: A server member
        args: Commentary on user
        """
        await self._getError(ctx, messages.stalker_err_not_implemented, pin=False)

    @database_update.command(name="nickname")
    async def database_update_nickname (self, ctx: commands.Context, member: discord.Member, *args):
        """Update user's nickname

        member: A server member
        args: A new nickname
        """
        await self._getError(ctx, messages.stalker_err_not_implemented, pin=False)

    @database_update.command(name="tempnickname")
    async def database_update_nickname (self, ctx: commands.Context, member: discord.Member, *args):
        """Update user's nickname

        member: A server member
        args: A new temporary nickname. If empty, reset to default
        """
        await self._getError(ctx, messages.stalker_err_not_implemented, pin=False)

    @database.command(name="statistics", aliases=["stats"])
    async def database_statistics (self, ctx: commands.Context):
        """Display statistics about known users"""
        await self._getError(ctx, messages.stalker_err_not_implemented, pin=False)

    @database.command(name="today")
    async def database_today (self, ctx: commands.Context):
        """Display the count of users that joined/were verified today"""
        await self._getError(ctx, messages.stalker_err_not_implemented, pin=False)        


    def _getEmbed (self, ctx: commands.Context, color: str = None, pin = False):
        if color not in [config.color_true, config.color_false]:
            color = config.color
        c = ctx.command
        p = ' '.join((p.name) for p in c.parents) + " " if c.parents else ""
        t = config.default_prefix + p + c.name
        if pin is not None and pin:
            t = "📌 " + t
        d = "**{}** cog".format(c.cog_name)
        embed = discord.Embed(color=color,
            title=t, description=d, delete_after=config.delay_embed)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        return embed

    async def _getError (self, ctx: commands.Context, errmsg: str,
                               delete: bool = True, pin: bool = None):
        """Show an error embed"""
        embed = self._getEmbed(ctx, color=config.color_false, pin = pin)
        embed.add_field(name="Error occured", value=errmsg, inline=False)
        embed.add_field(name="Command", value=ctx.message.content, inline=False)
        if delete:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        else:
            await ctx.send(embed=embed)
        await self._tryDelete(ctx, now=True)

    async def _getDescription (self, ctx: commands.Context):
        """Show description for command"""
        embed = self._getEmbed(ctx)
        embed.add_field(name="Description", value=ctx.command.short_doc)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx, now=True)

    async def _getHelp (self, ctx: commands.Context):
        """Show parameters for command"""
        #TODO add bold text to the first line and parameter names
        embed = self._getEmbed(ctx)
        embed.add_field(name="Help", value=ctx.command.help)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx, now=False)

    async def _getOptions (self, ctx: commands.Context):
        """Show commands available inside of a command group"""
        embed = self._getEmbed(ctx)
        if ctx.command.commands:
            for opt in ctx.command.commands:
                # ctx.command.commands are probably sorted as they are loaded,
                # eg. backwards. This is not 100% reliable, but it works,
                # generally
                embed.insert_field_at(index=0,
                    name=opt.name, value=opt.short_doc, inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx, now=True)

    async def _tryDelete (self, ctx: commands.Context, now: bool = False):
        """Try to delete the context message.

        now: On "now" string, do not wait for embed delay
        """
        try:
            if now:
                await ctx.message.delete()
            else:
                await ctx.message.delete(delay=config.delay_embed)
        except discord.HTTPException:
            pass

    #FIXME Can this be done in a dynamic way?
    def _parsePin (self, pin):
        return pin is not None and pin == "pin"
    def _parseForce (self, force):
        return force is not None and force == "force"

    #FIXME Can those be caucht on one line?
    @whois.error
    @database_add.error
    @database_remove.error
    @database_update.error
    @database_update_login.error
    @database_update_comment.error
    @database_update_status.error
    @database_update_group.error
    @database_update_nickname.error
    @database_statistics.error
    async def stalker_error (self, ctx, error):
        """Print error"""
        await self._getError(ctx, error, delete = False)

def setup(bot):
    bot.add_cog(Stalker(bot))
