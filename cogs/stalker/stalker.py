import random

import discord
from discord.ext import commands

from cogs.resource import CogText
from core import acl, rubbercog, utils
from core.config import config
from repository import acl_repo, user_repo

repository = user_repo.UserRepository()
repo_a = acl_repo.ACLRepository()


class Stalker(rubbercog.Rubbercog):
    """A cog for database lookups"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

        self.text = CogText("stalker")

    ##
    ## Commands
    ##

    @commands.check(acl.check)
    @commands.command()
    async def roleinfo(self, ctx, role: discord.Role):
        """Get information about role on current server"""
        # TODO Add permission list

        group = repo_a.get_group_by_role(role.id)

        embed = self.embed(ctx=ctx, title=role.name, description=role.id, color=role.color)
        embed.add_field(
            name="\u200b",
            value=self.text.get(
                "roleinfo",
                count=len(role.members),
                mentionable=role.mentionable,
                acl_group=group.name if group is not None else "---",
            ),
        )

        await ctx.send(embed=embed)

    @commands.check(acl.check)
    @commands.command(name="channelinfo")
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        topic = f"{channel.topic}\n" if channel.topic is not None else ""
        embed = self.embed(ctx=ctx, title=channel.name, description=f"{topic}{channel.id}")

        # gather information
        webhooks = await channel.webhooks()
        roles = []
        users = []
        for overwrite in channel.overwrites:
            if isinstance(overwrite, discord.Role):
                roles.append(overwrite)
            else:
                users.append(overwrite)

        # fill embed
        embed.add_field(
            name="\u200b",
            value=self.text.get(
                "channelinfo",
                count=len(channel.members),
                webhooks=len(webhooks),
                role_count=len(roles),
                user_count=len(users),
            ),
        )

        await ctx.send(embed=embed)

    @commands.check(acl.check)
    @commands.group(name="whois", aliases=["gdo"])
    async def whois(self, ctx: commands.Context):
        """Get information about user"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @whois.command(name="member", aliases=["tag", "user", "id"])
    async def whois_member(self, ctx: commands.Context, member: discord.Member):
        """Get information about guild member

        member: A guild member
        """
        db_member = repository.get(member.id)

        embed = self.whois_embed(ctx, member, db_member)

        await ctx.send(embed=embed)
        await self.event.sudo(ctx, f"Database lookup for member **{member}**.")

    @commands.check(acl.check)
    @whois.command(name="email", aliases=["login", "xlogin"])
    async def whois_email(self, ctx: commands.Context, email: str = None):
        """Get information about xlogin

        email: An e-mail
        """
        db_member = repository.getByLogin(email)
        if db_member is None:
            # TODO Should we raise MemberNotFound?
            return await self.output.info(ctx, self.text.get("not_found"))
        member = self.getGuild().get_member(db_member.discord_id)
        if member is None:
            return await self.output.info(ctx, self.text.get("not_in_guild"))

        embed = self.whois_embed(ctx, member, db_member)

        await ctx.send(embed=embed)
        await self.event.sudo(ctx, f"Database lookup for e-mail **{email}**.")

    @commands.check(acl.check)
    @whois.command(name="logins", aliases=["emails"])
    async def whois_logins(self, ctx, prefix: str):
        """Filter database by login"""
        users = repository.getByPrefix(prefix=prefix)

        # parse data
        items = []
        template = "`{name:<10}` … {email}"
        for user in users:
            member = self.bot.get_user(user.discord_id)
            name = member.name if member is not None else ""
            email = self.dbobj2email(user)
            items.append(template.format(name=name, email=email))

        # construct embed fields
        fields = []
        field = ""
        for item in items:
            if len(field + item) > 1000:
                fields.append(field)
                field = ""
            field = field + "\n" + item
        if len(field):
            fields.append(field)

        # create embed
        embed = self.embed(ctx=ctx, description=self.text.get("prefix", "result", num=len(users)))
        for field in fields[:5]:  # there is a limit of 6000 characters in total
            embed.add_field(name="\u200b", value=field)
        if len(fields) > 5:
            embed.add_field(
                name=self.text.get("prefix", "too_many"),
                value=self.text.get("prefix", "omitted"),
                inline=False,
            )

        await ctx.send(embed=embed)
        await self.event.sudo(ctx, f"Database lookup for e-mail prefix **{prefix}**.")

    @commands.check(acl.check)
    @commands.group(aliases=["db"])
    async def database(self, ctx: commands.Context):
        """Manage users"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @database.command(name="add")
    async def database_add(
        self,
        ctx: commands.Context,
        member: discord.Member,
        login: str,
        group: discord.Role,
    ):
        """Add user to database

        member: A server member
        login: e-mail
        group: A role from `roles_native` or `roles_guest` in config file
        """
        # define variables
        guild = self.bot.get_guild(config.guild_id)
        verify = discord.utils.get(guild.roles, name="VERIFY")

        if repository.get(member.id) is not None:
            return await self.output.error(ctx, self.text.get("db", "duplicate"))

        try:
            repository.add(
                discord_id=member.id,
                login=login,
                group=group.name,
                status="verified",
                code="MANUAL",
            )
        except Exception as e:
            return await self.output.error(ctx, self.text.get("db", "write_error"), e)

        # assign roles, if neccesary
        if verify not in member.roles:
            await member.add_roles(verify)
        if group not in member.roles:
            await member.add_roles(group)

        # display the result
        embed = self.whois_embed(ctx, member, repository.get(member.id))
        await ctx.send(embed=embed)
        await self.event.sudo(ctx, f"New member {member} ({group.name}).")

    @commands.check(acl.check)
    @database.command(name="add-missing", aliases=["add_missing"])
    async def database_add_missing(self, ctx, user_id: int, login: str, group: str):
        """Add user ID to database

        user_id: User ID or zero, if not known
        login: e-mail
        group: A role name
        """
        if repository.getByLogin(login) is not None:
            return await self.output.error(ctx, self.text.get("db", "duplicate"))

        # generate something random
        if user_id == 0:
            user_id = random.randint(1000000000, 9999999999)

        try:
            repository.add(discord_id=user_id, login=login, group=group, status="unknown", code="")
        except Exception as e:
            return await self.output.error(ctx, self.text.get("db", "write_error"), e)

        # display the result
        embed = self.whois_embed(ctx, None, repository.get(user_id))
        await ctx.send(embed=embed)
        await self.event.sudo(ctx, f"New virtual member **{user_id}**.")

    @commands.check(acl.check)
    @database.command(name="remove", aliases=["delete"])
    async def database_remove(self, ctx: commands.Context, member: discord.Member):
        """Remove user from database"""
        result = repository.deleteId(discord_id=member.id)

        if result < 1:
            return await self.output.error(ctx, self.text.get("db", "delete_error"))

        await ctx.send(self.text.get("db", "delete_success", num=result))
        await self.event.sudo(ctx, f"Member {member} ({member.id}) removed from database.")

    @commands.check(acl.check)
    @database.command(name="update")
    async def database_update(self, ctx, member: discord.Member, key: str, *, value):
        """Update user entry in database

        key: value
        - login: e-mail
        - group: one of the groups defined in gatekeeper mapping
        - status: [unknown, pending, verified, kicked, banned]
        - comment: commentary on user
        """
        if key not in ("login", "group", "status", "comment"):
            return await self.output.error(ctx, self.text.get("db", "invalid_key"))

        if key == "login":
            repository.update(member.id, login=value)

        elif key == "group":
            # get list of role names, defined in
            role_ids = config.get("roles", "native") + config.get("roles", "guests")
            role_names = [
                x.name
                for x in [self.getGuild().get_role(x) for x in role_ids]
                if hasattr(x, "name")
            ]
            value = value.upper()
            if value not in role_names:
                return await self.output.error(ctx, self.text.get("db", "invalid_value"))
            repository.update(member.id, group=value)

        elif key == "status":
            if value not in ("unknown", "pending", "verified", "kicked", "banned"):
                return await self.output.error(ctx, self.text.get("db", "invalid_value"))
            repository.update(member.id, status=value)

        elif key == "comment":
            repository.update(member.id, comment=value)

        await self.event.sudo(ctx, f"Updated {member}: {key} = {value}.")
        await ctx.send(self.text.get("db", "update_success"))

    @commands.check(acl.check)
    @database.command(name="show")
    async def database_show(self, ctx, param: str):
        """Filter users by parameter

        param: [unverified, pending, kicked, banned]
        """
        if param not in ("unverified", "pending", "kicked", "banned"):
            return await utils.send_help(ctx)

        await self._database_show_filter(ctx, param)

    @commands.check(acl.check)
    @commands.command(name="guild", aliases=["server"])
    async def guild(self, ctx: commands.Context):
        """Display general about guild"""
        embed = self.embed(ctx=ctx)
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

        await ctx.send(embed=embed)

    ##
    ## Helper functions
    ##

    async def _database_show_filter(self, ctx: commands.Context, status: str = None):
        """Helper function for all databas_show_* functions"""
        if status is None or status not in config.db_states:
            return await utils.send_help(ctx)

        users = repository.filterStatus(status=status)

        embed = self.embed(ctx=ctx)
        embed.add_field(name="Result", value="{} users found".format(len(users)), inline=False)
        if users:
            embed.add_field(name="-" * 60, value="LIST:", inline=False)
        for user in users:
            member = discord.utils.get(self.getGuild().members, id=user.discord_id)
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

    def whois_embed(self, ctx, member: discord.Member, db_member: object) -> discord.Embed:
        """Construct the whois embed"""
        embed = self.embed(
            ctx=ctx, title="Whois", description=member.mention if member is not None else "???"
        )

        if member is not None:
            embed.add_field(
                name=self.text.get("whois", "information"),
                value=self.text.get(
                    "whois",
                    "account_information",
                    name=self.sanitise(member.display_name),
                    account_since=utils.id_to_datetime(member.id).strftime("%Y-%m-%d"),
                    member_since=member.joined_at.strftime("%Y-%m-%d"),
                ),
                inline=False,
            )

        if db_member is not None:
            embed.add_field(
                name=self.text.get("whois", "login"),
                value=self.dbobj2email(db_member)
                if db_member.login
                else self.text.get("whois", "missing"),
            )

            embed.add_field(
                name=self.text.get("whois", "code"),
                value=db_member.code if db_member.code else self.text.get("whois", "missing"),
            )

            embed.add_field(
                name=self.text.get("whois", "status"),
                value=db_member.status if db_member.status else self.text.get("whois", "missing"),
            )

            embed.add_field(
                name=self.text.get("whois", "group"),
                value=db_member.group if db_member.group else self.text.get("whois", "missing"),
            )

            embed.add_field(
                name=self.text.get("whois", "changed"),
                value=db_member.changed if db_member.changed else self.text.get("whois", "missing"),
            )

            if db_member.comment and len(db_member.comment):
                embed.add_field(
                    name=self.text.get("whois", "comment"), value=db_member.comment, inline=False
                )

        if member is not None:
            role_list = ", ".join(list((r.name) for r in member.roles[::-1])[:-1])
            embed.add_field(
                name=self.text.get("whois", "roles"),
                value=role_list if len(role_list) else self.text.get("whois", "missing"),
            )

        return embed

    ##
    ## Helper functions
    ##

    def dbobj2email(self, user):
        if user is not None:
            if user.group == "FEKT" and "@" not in user.login:
                email = user.login + "@stud.feec.vutbr.cz"
            elif user.group == "VUT" and "@" not in user.login:
                email = user.login + "@vutbr.cz"
            else:
                email = user.login
            return email
        return
