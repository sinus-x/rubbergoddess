import discord
from discord.ext import commands
from datetime import datetime

from core import check, rubbercog, utils
from core.config import config
from core.text import text
from repository import user_repo

repository = user_repo.UserRepository()


class Stalker(rubbercog.Rubbercog):
    """A cog for database lookups"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    def dbobj2email(self, dbobj):
        if dbobj is not None:
            if dbobj.group == "FEKT":
                email = (
                    dbobj.login + "@stud.feec.vutbr.cz" if "@" not in dbobj.login else dbobj.login
                )
            elif dbobj.group == "VUT":
                email = dbobj.login + "@vutbr.cz" if "@" not in dbobj.login else dbobj.login
            else:
                email = dbobj.login
            return email
        return

    @commands.check(check.is_verified)
    @commands.group(name="whois", aliases=["gdo"])
    async def whois(self, ctx: commands.Context):
        """Get information about user"""
        await utils.send_help(ctx)

    @whois.command(name="member", aliases=["tag", "user", "id"])
    async def whois_member(
        self, ctx: commands.Context, member: discord.Member = None, log: bool = True
    ):
        """Get information about guild member

        member: A guild member
        pin: A "pin" string that will prevent the embed from disappearing
        """
        if member is None:
            return await utils.send_help(ctx)

        # get user from database
        try:
            dbobj = repository.filterId(discord_id=member.id)[0]
        except IndexError:
            dbobj = None

        embed = discord.Embed(color=config.color, title="Whois lookup", description=member.mention)
        ni = discord.utils.escape_markdown(member.nick) if member.nick else None
        na = discord.utils.escape_markdown(member.name)
        n = f"**{na}** (nick **{ni}**)" if ni else f"**{na}**"
        embed.add_field(
            name="Discord user data",
            value="{name}\n{d_id}\nMember since {date}".format(
                name=n, d_id=member.id, date=member.joined_at.strftime("%Y-%m-%d")
            ),
        )

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
            embed.add_field(
                inline=False, name="Status", value=dbobj.status if dbobj.status else "_none_"
            )
            if dbobj.comment is not None and len(dbobj.comment) > 0:
                embed.add_field(name="Comment", value=dbobj.comment, inline=False)

        role_list = ", ".join(list((m.name) for m in member.roles[::-1])[:-1])
        embed.add_field(
            inline=False, name="Roles", value=role_list if len(role_list) > 0 else "_none_"
        )

        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await self.event.user(ctx.author, ctx.channel, f"Database lookup for {member}")

        await utils.delete(ctx)

    @whois.command(name="login", aliases=["xlogin", "vutlogin"])
    @commands.check(check.is_elevated)
    async def whois_login(self, ctx: commands.Context, login: str = None, log: bool = True):
        """Get information about xlogin

        login: A xlogin
        """
        if login is None:
            return await utils.send_help(ctx)

        # get user from database
        try:
            dbobj = repository.filterLogin(login=login)[0]
            member = self.getGuild().get_member(dbobj.discord_id)
        except IndexError:
            member = None

        if member:
            await self.whois_member(ctx, member, log=True)
            return

        t = "Whois lookup"
        embed = discord.Embed(color=config.color, title=t)
        embed.add_field(name="Action unsuccessful", value="No user **{}** found.".format(login))
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await self.event.user(ctx.author, ctx.channel, f"Database lookup for {member}")

        await utils.delete(ctx)

    @commands.guild_only()
    @commands.group(aliases=["db"])
    @commands.check(check.is_elevated)
    async def database(self, ctx: commands.Context):
        """Manage users"""
        await utils.send_help(ctx)

    @database.command(name="add")
    async def database_add(
        self,
        ctx: commands.Context,
        member: discord.Member = None,
        login: str = None,
        group: discord.Role = None,
    ):
        """Add user to database

        member: A server member
        login: xlogin (FEKT, VUT) or e-mail
        group: A role from `roles_native` or `roles_guest` in config file
        """
        if member is None or login is None or group is None:
            return await utils.send_help(ctx)

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        verify = discord.utils.get(guild.roles, name="VERIFY")

        # try to write to database
        try:
            repository.filterId(discord_id=member.id)[0]
            await self.throwError(ctx, text.get("db", "duplicate"))
            return
        except IndexError:
            # no result is good, we won't have collision
            pass

        try:
            repository.add_user(
                discord_id=member.id,
                login=login,
                group=group.name,
                status="verified",
                code="MANUAL",
            )
        except Exception:
            await self.throwError(ctx, text.get("db", "write"))
            return

        # assign roles, if neccesary
        if verify not in member.roles:
            await member.add_roles(verify)
        if group not in member.roles:
            await member.add_roles(group)

        # display the result
        await self.whois_member(ctx, member, log=False)

        await self.event.sudo(ctx.author, ctx.channel, f"New user {member} ({group.name})")

    @database.command(name="remove", aliases=["delete"])
    async def database_remove(
        self, ctx: commands.Context, member: discord.Member = None, force: str = None
    ):
        """Remove user from database

        member: A server member
        force: "force" string. If omitted, show what will be deleted
        """
        if member is None:
            return await self.send_help(ctx)

        # define variables
        guild = self.bot.get_guild(config.guild_id)
        force = self.parseArg(force)

        try:
            if force:
                result = repository.deleteId(discord_id=member.id)
            else:
                result = repository.filterId(discord_id=member.id)
        except Exception:
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
            embed.add_field(
                inline=False, name="Success", value=text.fill("db", "delete success", num=result)
            )
            embed.add_field(name="Warning", value="Roles and channel access haven't been removed")
            await self.log(ctx, "Database entry removed", quote=True)
            # TODO remove all roles
        else:
            # simulate
            embed = discord.Embed(color=config.color_notify, title=t, description=d)
            for r in result:
                embed.add_field(
                    inline=False,
                    name=self.dbobj2email(r),
                    value=discord.utils.get(guild.members, id=int(r.discord_id)).mention,
                )
            if len(result) < 1:
                embed.add_field(name="No entry", value=text.get("db", "not found"), inline=False)
        embed.set_footer(text=ctx.author)
        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await utils.delete(ctx)

    @database.group(name="update")
    async def database_update(self, ctx: commands.Context):
        """Set of functions to update database entries"""
        await utils.send_help(ctx)

    @database_update.command(name="login")
    async def database_update_login(
        self, ctx: commands.Context, member: discord.Member, login: str
    ):
        """Update user's registered login

        member: A server member
        login: User's xlogin (FEKT, VUT) or e-mail
        """
        try:
            repository.update_login(discord_id=member.id, login=login)
            await ctx.send(text.get("db", "update success"))
            await self.event.sudo(ctx.author, ctx.channel, f"Login update for {member} ({login})")
            await utils.delete(ctx)
        except Exception as e:
            await self.throwError(ctx, e)

    @database_update.command(name="group")
    async def database_update_group(
        self, ctx: commands.Context, member: discord.Member, group: str
    ):
        """Update user's registered group

        member: A server member
        group: A role name
        """
        try:
            repository.update_group(discord_id=member.id, group=group)
            await ctx.send(text.get("db", "update success"))
            await self.event.sudo(ctx.author, ctx.channel, f"Group update for {member} ({group})")
            await utils.delete(ctx)
        except Exception as e:
            await self.throwError(ctx, e)

    @database_update.command(name="status")
    async def database_update_status(
        self, ctx: commands.Context, member: discord.Member, status: str
    ):
        """Update user's verification status

        member: A server member
        status: unknown, pending, verified, kicked, banned
        """
        try:
            repository.update_status(discord_id=member.id, status=status)
            await ctx.send(text.get("db", "update success"))
            await self.event.sudo(ctx.author, ctx.channel, f"Status update for {member} ({status})")
            await utils.delete(ctx)
        except Exception as e:
            await self.throwError(ctx, e)

    @database_update.command(name="comment")
    async def database_update_comment(
        self, ctx: commands.Context, member: discord.Member, *, comment: str
    ):
        """Update comment on user

        member: A server member
        args: Commentary on user
        """
        try:
            repository.update_comment(discord_id=member.id, comment=comment)
            await ctx.send(text.get("db", "update success"))
            await self.event.sudo(
                ctx.author, ctx.channel, f"Comment update for {member} ({comment})"
            )
            await utils.delete(ctx)
        except Exception as e:
            await self.throwError(ctx, e)

    @database.group(name="show")
    async def database_show(self, ctx: commands.Context):
        """Set of filter functions"""
        await utils.send_help(ctx)

    @database_show.command(name="unverified")
    async def database_show_unverified(self, ctx: commands.Context):
        """List users that have not yet requested verification code"""
        await self._database_show_filter(ctx, "unverified")

    @database_show.command(name="pending")
    async def database_show_pending(self, ctx: commands.Context):
        """List users that have not yet submitted the verification code"""
        await self._database_show_filter(ctx, "pending")

    @database_show.command(name="kicked")
    async def database_show_kicked(self, ctx: commands.Context):
        """List users that have been kicked"""
        await self._database_show_filter(ctx, "kicked")

    @database_show.command(name="banned")
    async def database_show_banned(self, ctx: commands.Context):
        """List users that have been banned"""
        await self._database_show_filter(ctx, "banned")

    @commands.guild_only()
    @commands.command(name="today")
    async def today(self, ctx: commands.Context):
        """Display the count of users that joined/were verified today"""

        # TODO count verified users with entry.roles
        ctr_usr_ver = 0  # noqa: F841
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

        embed = self._getEmbed(ctx)
        embed.add_field(name="Successful verifications", value="_(Not implemented)_")
        if ctr_usr_kic > 0:
            embed.add_field(name="Users kicked", value=ctr_usr_kic)
        if ctr_usr_ban > 0:
            embed.add_field(name="Users banned", value=ctr_usr_ban)
        if ctr_invites > 0:
            embed.add_field(name="Invites created", value=ctr_invites)
        embed.add_field(name="Messages pinned", value=ctr_msg_pin)

        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await utils.delete(ctx)

    @commands.guild_only()
    @commands.command(name="guild", aliases=["server"])
    async def guild(self, ctx: commands.Context):
        """Display general about guild"""
        embed = self._getEmbed(ctx)
        g = self.getGuild()

        # guild
        embed.add_field(
            name=f"Guild **{g.name}**",
            inline=False,
            value=f"Created {g.created_at.strftime('%Y-%m-%d')}," f" owned by **{g.owner.name}**",
        )

        # verification
        states = ", ".join(
            "**{}** {}".format(repository.countStatus(state), state) for state in config.db_states
        )
        embed.add_field(name="Verification states", value=states, inline=False)

        # roles
        role_ids = config.get("roles", "native") + config.get("roles", "guests")
        roles = []
        for role_id in role_ids:
            role = self.getGuild().get_role(role_id)
            if role is not None:
                roles.append(f"**{role}** {repository.countGroup(role.name)}")
            else:
                roles.append(f"**{role_id}** {repository.countGroup(role_id)}")
        roles = ", ".join(roles)
        embed.add_field(name="Roles", value=f"Total count {len(g.roles)}\n{roles}", inline=False)

        # channels
        embed.add_field(
            name=f"{len(g.categories)} categories",
            value=f"{len(g.text_channels)} text channels, {len(g.voice_channels)} voice channels",
        )

        # users
        embed.add_field(
            name="Users",
            value=f"Total count **{g.member_count}**, {g.premium_subscription_count} boosters",
        )

        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await utils.delete(ctx)

    async def _database_show_filter(self, ctx: commands.Context, status: str = None, pin=False):
        """Helper function for all databas_show_* functions"""
        if status is None or status not in config.db_states:
            self.throwHelp(ctx)
            return

        guild = self.bot.get_guild(config.guild_id)

        users = repository.filterStatus(status=status)

        embed = self._getEmbed(ctx)
        embed.add_field(name="Result", value="{} users found".format(len(users)), inline=False)
        if users:
            embed.add_field(name="-" * 60, value="LIST:", inline=False)
        for user in users:
            member = discord.utils.get(guild.members, id=user.discord_id)
            if member:
                name = "**{}**, {}".format(member.name, member.id)
            else:
                name = "**{}**, {} _(not on server)_".format(user.discord_id, user.group)
            d = user.changed
            date = (d[:4] + "-" + d[4:6] + "-" + d[6:]) if (d and len(d) == 8) else "_(none)_"
            embed.add_field(
                name=name, value="{}\nLast action on {}".format(self.dbobj2email(user), date)
            )

        await ctx.send(embed=embed, delete_after=config.delay_embed)

        await utils.delete(ctx)


def setup(bot):
    bot.add_cog(Stalker(bot))
