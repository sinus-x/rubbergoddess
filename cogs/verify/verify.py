import random
import re
import smtplib
import string

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from core.config import config
from repository import user_repo

repo_u = user_repo.UserRepository()


class Verify(rubbercog.Rubbercog):
    """Verify your account"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("verify")
        self.config = CogConfig("verify")

    ##
    ## Commands
    ##

    @commands.check(acl.check)
    @commands.cooldown(rate=5, per=120, type=commands.BucketType.user)
    @commands.command()
    async def verify(self, ctx, email: str):
        """Ask for verification code"""
        await utils.delete(ctx)

        if email.count("@") != 1:
            raise NotAnEmail()

        if self.config.get("placeholder") in email:
            raise PlaceholderEmail()

        # check the database for member ID
        if repo_u.get(ctx.author.id) is not None:
            raise IDAlreadyInDatabase()

        # check the database for email
        if repo_u.getByLogin(email) is not None:
            raise EmailAlreadyInDatabase()

        # check e-mail format
        role = await self._email_to_role(ctx, email)

        # generate code
        code = await self._add_user(ctx.author, login=email, role=role)

        # send mail
        try:
            await self._send_verification_email(ctx.author, email, code)
        except smtplib.SMTPServerDisconnected:
            await self.output.warning(ctx, "SMTP server disconnected, trying for the second time.")
            await self._send_verification_email(ctx.author, email, code)

        anonymised = "[redacted]@" + email.split("@")[1]
        await ctx.send(
            self.text.get(
                "verify successful",
                mention=ctx.author.mention,
                email=anonymised,
                prefix=config.prefix,
            ),
            delete_after=config.get("delay", "verify"),
        )

    @commands.check(acl.check)
    @commands.cooldown(rate=3, per=120, type=commands.BucketType.user)
    @commands.command()
    async def submit(self, ctx, code: str):
        """Submit verification code"""
        await utils.delete(ctx)

        db_user = repo_u.get(ctx.author.id)

        if db_user is None or db_user.status in ("unknown", "unverified") or db_user.code is None:
            raise SubmitWithoutCode()

        if db_user.status != "pending":
            raise ProblematicVerification(status=db_user.status, login=db_user.login)

        # repair the code
        code = code.replace("I", "1").replace("O", "0").upper()
        if code != db_user.code:
            raise WrongVerificationCode(ctx.author, code, db_user.code)

        # user is verified now
        repo_u.save_verified(ctx.author.id)

        # add role
        await self._add_verify_roles(ctx.author, db_user)

        # send messages
        for role_id in config.get("roles", "native"):
            if role_id in [x.id for x in ctx.author.roles]:
                await ctx.author.send(self.text.get("verification DM native"))
                break
        else:
            await ctx.author.send(self.text.get("verification DM guest"))
        # fmt: off
        # announce the verification
        await ctx.channel.send(self.text.get(
                "verification public",
                mention=ctx.author.mention,
                role=db_user.group,
        ), delete_after=config.get("delay", "verify"))
        # fmt: on

        await self.event.user(
            ctx,
            f"User {ctx.author.id} verified with group **{db_user.group}**.",
        )

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Add them their roles back, if they have been verified before"""
        if member.guild.id != config.guild_id:
            return

        db_user = repo_u.get(member.id)
        if db_user is None or db_user.status != "verified":
            return

        # user has been verified, give them their main roles back
        await self._add_verify_roles(member, db_user)
        await self.event.user(member, f"Verification skipped (**{db_user.group}**)")

    ##
    ## Helper functions
    ##

    async def _email_to_role(self, ctx, email: str) -> discord.Role:
        """Get role from email address"""
        registered = self.config.get("suffixes")
        constraints = self.config.get("constraints")
        username = email.split("@")[0]

        for domain, role_id in list(registered.items())[:-1]:
            if not email.endswith(domain):
                continue
            # found corresponding domain, check constraint
            if domain in constraints:
                constraint = constraints[domain]
            else:
                constraint = list(constraints.values())[-1]
            match = re.fullmatch(constraint, username)
            # return
            if match is not None:
                return self.getGuild().get_role(role_id)
            else:
                await self.event.user(ctx, f"Rejecting e-mail: {self.sanitise(email)}")
                raise BadEmail(constraint=constraint)

        # domain not found, fallback to basic guest role
        role_id = registered.get(".")
        constraint = list(constraints.values())[-1]
        match = re.fullmatch(constraint, username)
        # return
        if match is not None:
            return self.getGuild().get_role(role_id)
        else:
            await self.event.user(ctx, f"Rejecting e-mail: {self.sanitise(email)}")
            raise BadEmail(constraint=constraint)

    async def _add_user(self, member: discord.Member, login: str, role: discord.Role) -> str:
        code_source = string.ascii_uppercase.replace("O", "").replace("I", "") + string.digits
        code = "".join(random.choices(code_source, k=8))

        repo_u.add(discord_id=member.id, login=login, group=role.name, code=code)
        await self.event.user(
            member, f"Adding {member.id} to database (**{role.name}**, code `{code}`)."
        )
        return code

    async def _update_user(self, member: discord.Member) -> str:
        code_source = string.ascii_uppercase.replace("O", "").replace("I", "") + string.digits
        code = "".join(random.choices(code_source, k=8))

        repo_u.update(discord_id=member.id, code=code, status="pending")
        await self.event.user(member, f"{member.id} updated with code `{code}`")
        return code

    async def _send_verification_email(self, member: discord.Member, email: str, code: str) -> bool:
        cleartext = self.text.get("plaintext mail").format(
            guild_name=self.getGuild().name,
            code=code,
            bot_name=self.bot.user.name,
            git_hash=utils.git_get_hash()[:7],
            prefix=config.prefix,
        )

        richtext = self.text.get(
            "html mail",
            # styling
            color_bg="#54355F",
            color_fg="white",
            font_family="Arial,Verdana,sans-serif",
            # names
            guild_name=self.getGuild().name,
            bot_name=self.bot.user.name,
            user_name=member.name,
            # codes
            code=code,
            git_hash=utils.git_get_hash()[:7],
            prefix=config.prefix,
            # images
            bot_avatar=self.bot.user.avatar_url_as(static_format="png", size=128),
            bot_avatar_size="120px",
            user_avatar=member.avatar_url_as(static_format="png", size=32),
            user_avatar_size="20px",
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = self.text.get(
            "mail subject", guild_name=self.getGuild().name, user_name=member.name
        )
        msg["From"] = self.config.get("email", "address")
        msg["To"] = email
        msg["Bcc"] = self.config.get("email", "address")
        msg.attach(MIMEText(cleartext, "plain"))
        msg.attach(MIMEText(richtext, "html"))

        with smtplib.SMTP(
            self.config.get("email", "server"), self.config.get("email", "port")
        ) as server:
            server.starttls()
            server.ehlo()
            server.login(self.config.get("email", "address"), self.config.get("email", "password"))
            server.send_message(msg)

    async def _add_verify_roles(self, member: discord.Member, db_user: object):
        """Return True if reverified"""
        verify = self.getVerifyRole()
        group = discord.utils.get(self.getGuild().roles, name=db_user.group)

        await member.add_roles(verify, group, reason="Verification")

    ##
    ## Error catching
    ##

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # try to get original error
        if hasattr(ctx.command, "on_error") or hasattr(ctx.command, "on_command_error"):
            return
        error = getattr(error, "original", error)

        # non-rubbergoddess exceptions are handled globally
        if not isinstance(error, rubbercog.RubbercogException):
            return

        # fmt: off
        # exceptions with parameters
        if isinstance(error, ProblematicVerification):
            await self.output.warning(
                ctx,
                self.text.get("ProblematicVerification", status=error.status)
            )

            await self.event.user(
                ctx,
                f"Problem with verification: {error.login}: {error.status}"
            )

        elif isinstance(error, BadEmail):
            await self.output.warning(
                ctx,
                self.text.get("BadEmail", constraint=error.constraint)
            )

        elif isinstance(error, WrongVerificationCode):
            await self.output.warning(
                ctx,
                self.text.get("WrongVerificationCode", mention=ctx.author.mention)
            )

            await self.event.user(
                ctx,
                f"User ({error.login}) code mismatch: `{error.their}` != `{error.database}`"
            )

        # exceptions without parameters
        elif isinstance(error, VerificationException):
            await self.output.error(ctx, self.text.get(type(error).__name__))
        # fmt: on


##
## Exceptions
##


class VerificationException(rubbercog.RubbercogException):
    pass


class NotInDatabase(VerificationException):
    pass


class NotAnEmail(VerificationException):
    pass


class PlaceholderEmail(VerificationException):
    pass


class AlreadyInDatabase(VerificationException):
    pass


class EmailAlreadyInDatabase(AlreadyInDatabase):
    pass


class IDAlreadyInDatabase(AlreadyInDatabase):
    pass


class BadEmail(VerificationException):
    def __init__(self, message: str = None, constraint: str = None):
        super().__init__(message)
        self.constraint = constraint


class UnexpectedReverify(VerificationException):
    pass


class SubmitWithoutCode(VerificationException):
    pass


class ProblematicVerification(VerificationException):
    def __init__(self, status: str, login: str):
        super().__init__()
        self.status = status
        self.login = login


class WrongVerificationCode(VerificationException):
    def __init__(self, member: discord.Member, login: str, their: str, database: str):
        super().__init__()
        self.member = member
        self.login = login
        self.their = their
        self.database = database
