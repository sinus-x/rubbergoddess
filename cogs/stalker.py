import discord
from discord.ext import commands
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

from core import config, emote, check, rubbercog, text, utils
from repository import user_repo
from repository.database import database
from repository.database import session

repository = user_repo.UserRepository()

class Stalker (rubbercog.Rubbercog):
    """A cog for database lookups"""

    def __init__ (self, bot: commands.Bot):
        super().__init__(bot)

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


    @commands.check(check.is_verified)
    @commands.command(name="whois", aliases=["stalk"])
    async def whois (self, ctx: commands.Context, member: discord.Member = None, 
                           pin = None, log: bool = True):
        """Get information about user

        member: A server member
        pin: A "pin" string that will prevent the embed from disappearing
        """
        if member is None:
            await self.throwHelp(ctx)
            await self.deleteCommand(ctx, now=True)
            return

        # define variables
        guild = ctx.guild
        pin = self.parseArg(pin)
        # get user from database
        try:
            dbobj = repository.filterId (discord_id=member.id)[0]
        except IndexError:
            dbobj = None
        
        t = "📌 " if pin else ""
        t += config.prefix + ctx.command.name
        embed = discord.Embed(color=config.color,
            title=t, description=member.mention)
        n = "**{} ({})**".format(member.nick, member.name) \
            if member.nick is not None else "**{}**".format(member.name)
        embed.add_field(name="Discord user data",
            value="{name}\n{d_id}\nMember since {date}".format(
                name=n, d_id=member.id, date=member.joined_at.strftime("%Y-%m-%d")))

        # do not display sensitive information in public channels
        if dbobj is not None and ctx.channel.id == config.channel_mods:
            # private channel, found in database
            email = self.dbobj2email(dbobj)
            if dbobj.changed and len(dbobj.changed) == 8:
                d = dbobj.changed
                date = d[:4] + "-" + d[4:6] + "-" + d[6:]
            elif dbobj.changed:
                date = dbobj.changed
            else:
                date = "_none_"
            embed.add_field(name="E-mail", value=email if email else "_none_", inline=False)
            embed.add_field(name="Verification code", value=dbobj.code if dbobj.code else "_none_")
            embed.add_field(name="Status", value=dbobj.status if dbobj.status else "_none_")
            embed.add_field(name="Last changed", value=date)
            if dbobj.comment is not None and len(dbobj.comment) > 0:
                embed.add_field(name="Comment", value=dbobj.comment, inline=False)

        elif not dbobj and ctx.channel.id == config.channel_mods:
            # private channel, not found
            embed.add_field(name="Not in database", value="Server only", inline=False)

        elif dbobj is not None and ctx.channel.id != config.channel_mods:
            # public channel
            embed.add_field(inline=False,
                name="Status", value=dbobj.status if dbobj.status else "_none_")
            if dbobj.comment is not None and len(dbobj.comment) > 0:
                embed.add_field(name="Comment", value=dbobj.comment, inline=False)

        role_list = ', '.join(list((m.name) for m in member.roles[::-1])[:-1])
        embed.add_field(inline=False,
            name="Roles", value=role_list if len(role_list) > 0 else "_none_")

        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        if log != False:
            await self.log(ctx, "Database entry lookup", quote=True)
        await self.deleteCommand(ctx, now=True)


    @commands.guild_only()
    @commands.group(aliases=["db"])
    @commands.check(check.is_mod)
    async def database (self, ctx: commands.Context):
        """Manage users"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)


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
            await self.throwHelp(ctx)
            return

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        verify = discord.utils.get(guild.roles, name="VERIFY")

        # try to write to database
        try:
            result = repository.filterId (discord_id=member.id)[0]
            await self.throwError(ctx, text.get("db", "duplicate"))
            return
        except IndexError:
            # no result is good, we won't have collision
            pass

        try:
            repository.add_user(discord_id=member.id, login=login,
                            group=group.name, status="verified", code="MANUAL")
        except Exception:
            await self.throwError(ctx, text.get("db", "write"))
            return

        # assign roles, if neccesary
        if verify not in member.roles:
            await member.add_roles(verify)
        if group not in member.roles:
            await member.add_roles(group)

        # display the result
        await self.log(ctx, "Database entry added", quote=True)
        await self.whois(ctx, member, log=False)
        

    @database.command(name="remove", aliases=["delete"])
    async def database_remove (self, ctx: commands.Context,
                                     member: discord.Member = None, force: str = None):
        """Remove user from database

        member: A server member
        force: "force" string. If omitted, show what will be deleted
        """
        if member is None:
            await self.throwHelp(ctx)
            return

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        force = self.parseArg(force)

        try:
            if force:
                result = repository.deleteId(discord_id=member.id)
            else:
                result = repository.filterId(discord_id=member.id)
        except Exception as e:
            await self.throwError(ctx, text.get("db", "read"))
            return

        t = self._getEmbedTitle(ctx)
        d = "Result" if force else "Simulation, run with `force` to apply"
        if force:
            embed = discord.Embed(color=config.color_success, title=t, description=d)
            # delete
            if result is None or result < 1:
                await self.throwError(ctx, text.get("db", "delete error"))
                return
            embed.add_field(inline=False,
                name="Success", value=text.fill("db", "delete success", num=result))
            embed.add_field(name="Warning", value="Roles and channel access haven't been removed")
            await self.log(ctx, "Database entry removed", quote=True)
            #TODO remove all roles
        else:
            # simulate
            embed = discord.Embed(color=config.color_notify, title=t, description=d)
            for r in result:
                embed.add_field(inline=False,
                    name=self.dbobj2email(r),
                    value=discord.utils.get(guild.members, id=int(r.discord_id)).mention)
            if len(result) < 1:
                embed.add_field(name="No entry", value=text.get("db", "not found"), inline=False)
        embed.set_footer(text=ctx.author)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx)


    @database.group(name="update")
    async def database_update (self, ctx: commands.Context):
        """Set of functions to update database entries"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)


    @database_update.command(name="login")
    async def database_update_login (self, ctx: commands.Context,
                                     member: discord.Member = None,
                                     login: str = None):
        """Update user's registered login

        member: A server member
        login: User's xlogin (FEKT, VUT) or e-mail
        """
        if member is None or login is None:
            await self.throwHelp(ctx)
            return

        try:
            repository.update_login(discord_id=member.id, login=login)
            await ctx.send(text.get("db", "update success"))
            await self.log(ctx, "Database entry updated (login)", quote=True)
            await self.deleteCommand(ctx)
        except Exception as e:
            await self.throwError(ctx, e)


    @database_update.command(name="group")
    async def database_update_group (self, ctx: commands.Context,
                                     member: discord.Member = None,
                                     group: discord.Role = None):
        """Update user's registered group

        member: A server member
        group: A role from `roles_native` or `roles_guest` in config file
        """
        if member is None or group is None:
            await self.throwHelp(ctx)
            return

        try:
            repository.update_group(discord_id=member.id, group=group)
            await ctx.send(text.get("db", "update success"))
            await self.log(ctx, "Database entry updated (group)", quote=True)
        except Exception as e:
            await self.throwError(ctx, e)
        await self.deleteCommand(ctx)


    @database_update.command(name="status")
    async def database_update_status (self, ctx: commands.Context,
                                      member: discord.Member = None,
                                      status: str = None):
        """Update user's verification status

        member: A server member
        status: unknown, pending, verified, kicked, banned
        """
        if member is None or status is None or status not in config.db_states:
            await self.throwHelp(ctx)
            return

        try:
            repository.update_status(discord_id=member.id, status=status)
            await ctx.send(text.get("db", "update success"))
            await self.log(ctx, "Database entry updated (status)", quote=True)
        except Exception as e:
            await self.throwError(ctx, e)
        await self.deleteCommand(ctx)


    @database_update.command(name="comment")
    async def database_update_comment (self, ctx: commands.Context,
                                       member: discord.Member = None, *args):
        """Update comment on user

        member: A server member
        args: Commentary on user
        """
        if member is None:
            await self.throwHelp(ctx)
            return

        comment = ' '.join(args) if args else ''
        try:
            repository.update_comment(discord_id=member.id, comment=comment)
            await ctx.send(text.get("db", "update success"))
            await self.log(ctx, "Database entry updated (comment)", quote=True)
        except Exception as e:
            await self.throwError(ctx, e)
        await self.deleteCommand(ctx)


    @database.group(name="show")
    async def database_show (self, ctx: commands.Context):
        """Set of filter functions"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)


    @database_show.command(name="unverified")
    async def database_show_unverified (self, ctx: commands.Context, pin=False):
        """List users that have not yet requested verification code"""
        await self._database_show_filter(ctx, "unverified", pin)


    @database_show.command(name="pending")
    async def database_show_pending (self, ctx: commands.Context, pin=False):
        """List users that have not yet submitted the verification code"""
        await self._database_show_filter(ctx, "pending", pin)


    @database_show.command(name="kicked")
    async def database_show_kicked (self, ctx: commands.Context, pin=False):
        """List users that have been kicked"""
        await self._database_show_filter(ctx, "kicked", pin)


    @database_show.command(name="banned")
    async def database_show_banned (self, ctx: commands.Context, pin=False):
        """List users that have been banned"""
        await self._database_show_filter(ctx, "banned", pin)


    @commands.guild_only()
    @commands.command(name="today")
    async def today (self, ctx: commands.Context, pin=False):
        """Display the count of users that joined/were verified today"""
        pin = self.parseArg(pin)

        ctr_usr_ver = 0 #TODO count verified users with entry.roles
        ctr_usr_kic = 0
        ctr_usr_ban = 0
        ctr_invites = 0
        ctr_msg_pin = 0
        try:
            async for entry in self.getGuild().audit_logs(after=datetime.now()):
                if entry.action == discord.AuditLogAction.kick:
                    ctr_usr_kic += 1
                elif entry.action == discord.AuditLogAction.ban:
                    ctr_usr_ban += 1
                elif entry.action == discord.AuditLogAction.invite_create:
                    ctr_invites += 1
                elif entry.action == discord.AuditLogAction.message_pin:
                    ctr_msg_pin += 1
        except discord.Forbidden as err:
            await self.throwError(ctx, err)
            await self.deleteCommand(ctx)
            return
        except discord.HTTPException as err:
            await self.throwError(ctx, err)
            await self.deleteCommand(ctx)
            return

        embed = self._getEmbed(ctx, pin=pin)
        embed.add_field(name="Successful verifications", value="_(Not implemented)_")
        if ctr_usr_kic > 0:
            embed.add_field(name="Users kicked", value=ctr_usr_kic)
        if ctr_usr_ban > 0:
            embed.add_field(name="Users banned", value=ctr_usr_ban)
        if ctr_invites > 0:
            embed.add_field(name="Invites created", value=ctr_invites)
        embed.add_field(name="Messages pinned", value=ctr_msg_pin)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx)


    @commands.guild_only()
    @commands.command(name="guild", aliases=["server"])
    async def guild (self, ctx: commands.Context, pin=False):
        """Display general about guild"""
        pin = self.parseArg(pin)
        embed = self._getEmbed(ctx, pin=pin)
        g = self.getGuild()

        # guild
        desc = "Created {}, {} boosters"
        embed.add_field(name=f"Guild **{g.name}**", inline=False,
            value=f"Created {g.created_at.strftime('%Y-%m-%d')},"
            f" owned by **{g.owner.mention}**")
        # verification
        states = ', '.join("**{}** {}".format(
            repository.countStatus(state), state) for state in config.db_states)
        embed.add_field(name="Verification states", value=states, inline=False)
        # roles
        groups = ', '.join("**{}** {}".format(group, repository.countGroup(group)) \
            for group in (config.roles_native + config.roles_guest))
        embed.add_field(name="Roles", value=f"Total count {len(g.roles)}\n{groups}", inline=False)
        # channels
        embed.add_field(name=f"{len(g.categories)} categories",
            value=f"{len(g.text_channels)} text channels, {len(g.voice_channels)} voice channels")
        # users
        embed.add_field(name="Users",
            value=f"Total count **{g.member_count}**, {g.premium_subscription_count} boosters")

        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx)


    async def _database_show_filter (self, ctx: commands.Context, status: str = None, pin=False):
        """Helper function for all databas_show_* functions"""
        if status is None or status not in config.db_states:
            self.throwHelp(ctx)
            return

        pin = self.parseArg(pin)
        guild = self.bot.get_guild(config.guild_id)

        users = repository.filterStatus(status=status)
        
        embed = self._getEmbed(ctx, pin=pin)
        embed.add_field(name="Result", value="{} users found".format(len(users)), inline=False)
        if users:
            embed.add_field(name="-"*60, value="LIST:", inline=False)
        for user in users:
            member = discord.utils.get(guild.members, id=user.discord_id)
            if member:
                name = "__{}__, {}".format(member.name, member.id)
            else:
                name = "{} _(not on server)_".format(user.discord_id, user.group)
            d = user.changed
            date = (d[:4] + "-" + d[4:6] + "-" + d[6:]) if (d and len(d) == 8) else "_(none)_"
            embed.add_field(name=name, value="{}\nLast action on {}".format(
                self.dbobj2email(user), date))
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx)


def setup(bot):
    bot.add_cog(Stalker(bot))
