import random
import re
import smtplib
import string

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import discord
from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from core.text import text
from repository import user_repo

repo_u = user_repo.UserRepository()


class Gatekeeper(rubbercog.Rubbercog):
    """Verify your account"""

    def __init__(self, bot):
        super().__init__(bot)

    ##
    ## Commands
    ##

    @commands.check(check.is_in_jail)
    @commands.check(check.is_not_verified)
    @commands.cooldown(rate=5, per=120, type=commands.BucketType.user)
    @commands.command()
    async def verify(self, ctx, email: str):
        """Ask for verification code"""
        if "@" not in email or len(email.split("@")) > 2:
            raise NotAnEmail()

        # check the database for member ID
        if repo_u.get(ctx.author.id) is not None:
            raise IDAlreadyInDatabase()

        # check the database for email
        if repo_u.getByLogin(email) is not None:
            raise EmailAlreadyInDatabase()

        # check e-mail format
        role = await self._email_to_role(ctx, email)

        # generate code
        code = self._add_user(ctx.author, login=email, role=role)

        # send mail
        await self._send_verification_email(ctx.author, email, code)
        anonymised = "[redacted]@" + email.split("@")[1]
        await ctx.send(
            text.fill(
                "gatekeeper",
                "verify successful",
                mention=ctx.author.mention,
                email=anonymised,
                prefix=config.prefix,
            ),
            delete_after=config.get("delay", "verify"),
        )

        await utils.delete(ctx)

    @commands.check(check.is_in_quarantine_or_dm)
    @commands.check(check.is_quarantined)
    @commands.cooldown(rate=5, per=120, type=commands.BucketType.user)
    @commands.group(name="reverify")
    async def reverify(self, ctx):
        await utils.send_help(ctx)

    @reverify.command(name="change", aliases=["update", "downgrade", "upgrade"])
    async def reverify_change(self, ctx, email: str):
        """Change your e-mail

        email: Your new verification e-mail
        """
        if "@" not in email or len(email.split("@")) > 2:
            raise NotAnEmail()

        # check if user is in database
        if repo_u.get(ctx.author.id) is None:
            raise NotInDatabase()

        # check the database for email
        if repo_u.getByLogin(email) is not None:
            raise EmailAlreadyInDatabase()

        role = await self._email_to_role(ctx, email)
        repo_u.update(discord_id=ctx.author.id, group=role.name)

        await self.output.info(ctx, "Mail changed")

        await utils.delete(ctx)

    @reverify.command(name="prove")
    async def reverify_prove(self, ctx):
        """Ask for verification code"""
        db_user = repo_u.get(ctx.author.id)

        if db_user is None:
            await self.console.error("User in `?reverify prove` is not in database.")
            raise NotInDatabase()

        if db_user.status != "quarantined":
            await self.console.error("User in `?reverify prove` did not have `quarantined` status.")
            raise UnexpectedReverify()

        if db_user.group == "FEKT" and "@" not in db_user.login:
            email = db_user.login + "@stud.feec.vutbr.cz"
        elif db_user.group == "VUT" and "@" not in db_user.login:
            email = db_user.login + "@vutbr.cz"
        else:
            email = db_user.login

        # generate new code
        code = self._update_user(ctx.author)

        # send mail
        await self._send_verification_email(ctx.author, email, code)

        await ctx.send(
            text.fill("gatekeeper", "reverify successful", mention=ctx.author.mention),
            delete_after=config.get("delay", "verify"),
        )

        await utils.delete(ctx)

    @commands.check(check.is_not_verified)
    @commands.cooldown(rate=3, per=120, type=commands.BucketType.user)
    @commands.command()
    async def submit(self, ctx, code: str):
        """Submit verification code"""
        await utils.delete(ctx)

        db_user = repo_u.get(ctx.author.id)

        if (
            db_user is None
            or db_user.status in ("unknown", "unverified", "quarantined")
            or db_user.code is None
        ):
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
        unverified = await self._add_verify_roles(ctx.author, db_user)
        if unverified:
            return await ctx.send(
                text.fill("gatekeeper", "reverification public", mention=ctx.author.mention),
                delete_after=config.get("delay", "verify"),
            )

        # send messages
        role_channel = self.getGuild().get_channel(config.get("channels", "bot_roles"))
        info_channel = self.getGuild().get_channel(config.get("channels", "info"))
        # fmt: off
        for role_id in config.get("roles", "native"):
            if role_id in [x.id for x in ctx.author.roles]:
                await ctx.author.send(text.fill(
                    "gatekeeper",
                    "verification DM native",
                    add_roles=role_channel.mention,
                    info=info_channel.mention,
                ))
                break
        else:
            await ctx.author.send(text.fill(
                "gatekeeper",
                "verification DM guest",
                add_roles=role_channel.mention,
                info=info_channel.mention,
            ))
        # announce the verification
        await ctx.channel.send(text.fill(
                "gatekeeper",
                "verification public",
                mention=ctx.author.mention,
                role=db_user.group,
        ), delete_after=config.get("delay", "verify"))
        # fmt: on
        if db_user.group == "TEACHER":
            await self.event.user(ctx.author, ctx.channel, "New teacher")

    ##
    ## Helper functions
    ##
    async def _email_to_role(self, ctx, email: str) -> discord.Role:
        """Get role from email address"""
        registered = config.get("gatekeeper", "suffixes")
        constraints = config.get("gatekeeper", "constraints")
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
                await self.event.user(ctx.author, ctx.channel, f"Rejecting e-mail: {email}")
                raise BadEmail(constraint=constraint)

        # domain not found, fallback to basic guest role
        role_id = registered.get(".")
        constraint = list(constraints.values())[-1]
        match = re.fullmatch(constraint, username)
        # return
        if match is not None:
            return self.getGuild().get_role(role_id)
        else:
            raise BadEmail(constraint=constraint)

    def _add_user(self, member: discord.Member, login: str, role: discord.Role) -> str:
        code_source = string.ascii_uppercase.replace("O", "").replace("I", "") + string.digits
        code = "".join(random.choices(code_source, k=8))

        repo_u.add(discord_id=member.id, login=login, group=role.name, code=code)
        return code

    def _update_user(self, member: discord.Member) -> str:
        code_source = string.ascii_uppercase.replace("O", "").replace("I", "") + string.digits
        code = "".join(random.choices(code_source, k=8))

        repo_u.update(discord_id=member.id, code=code, status="pending")
        return code

    async def _send_verification_email(self, member: discord.Member, email: str, code: str) -> bool:
        cleartext = text.get("gatekeeper", "plaintext mail").format(
            guild_name=self.getGuild().name,
            code=code,
            bot_name=self.bot.user.name,
            git_hash=utils.git_hash()[:7],
            prefix=config.prefix,
        )

        richtext = text.get("gatekeeper", "html mail").format(
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
            git_hash=utils.git_hash()[:7],
            prefix=config.prefix,
            # images
            bot_avatar=self.bot.user.avatar_url_as(static_format="png", size=128),
            bot_avatar_size="120px",
            user_avatar=member.avatar_url_as(static_format="png", size=32),
            user_avatar_size="20px",
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = text.fill(
            "gatekeeper", "mail subject", guild_name=self.getGuild().name, user_name=member.name
        )
        msg["From"] = config.get("email", "address")
        msg["To"] = email
        msg["Bcc"] = config.get("email", "address")
        msg.attach(MIMEText(cleartext, "plain"))
        msg.attach(MIMEText(richtext, "html"))

        with smtplib.SMTP(config.get("email", "server"), config.get("email", "port")) as server:
            server.starttls()
            server.ehlo()
            server.login(config.get("email", "address"), config.get("email", "password"))
            server.send_message(msg)

    async def _add_verify_roles(self, member: discord.Member, db_user: object) -> bool:
        """Return True if reverified"""
        verify = self.getVerifyRole()
        quarantine = self.getGuild().get_role(config.get("roles", "quarantine_id"))
        group = discord.utils.get(self.getGuild().roles, name=db_user.group)

        unverified = False
        if quarantine in member.roles:
            await member.remove_roles(quarantine, reason="Successful reverification")
            unverified = True

        await member.add_roles(verify, group, reason="Successful verification")
        return unverified

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
            await self.output.error(ctx, text.fill(
                "gatekeeper", "ProblematicVerification", status=error.status))

            await self.event.user(
                ctx.author, ctx.location,
                f"Problem with verification: {error.login}: {error.status}"
            )

        elif isinstance(error, BadEmail):
            await self.output.error(ctx, text.fill(
                "gatekeeper", "BadEmail", constraint=error.constraint))

        elif isinstance(error, WrongVerificationCode):
            await self.output.error(ctx, text.fill(
                "gatekeeper", "WrongVerificationCode", mention=ctx.author.mention))

            await self.event.user(
                ctx.author, ctx.channel,
                f"User ({error.login}) code mismatch: `{error.their}` != `{error.database}`"
            )

        # exceptions without parameters
        elif isinstance(error, VerificationException):
            await self.output.error(ctx, text.get("gatekeeper", type(error).__name__))
        # fmt: on


def setup(bot):
    bot.add_cog(Gatekeeper(bot))


##
## Exceptions
##


class VerificationException(rubbercog.RubbercogException):
    pass


class NotInDatabase(VerificationException):
    pass


class NotAnEmail(VerificationException):
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
