import random
import re
import smtplib
import string

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import discord
from discord.ext import commands

from core import check, exceptions, rubbercog, utils
from core.config import config
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
        if "@" not in email:
            raise exceptions.NotAnEmail()

        # check the database for member ID
        if repo_u.get(ctx.author.id) is not None:
            raise exceptions.IDAlreadyInDatabase()

        # check the database for email
        if repo_u.get(email) is not None:
            raise exceptions.EmailAlreadyInDatabase()

        # check e-mail format
        role = self._email_to_role(email)

        # generate code
        code = self._generate_and_save_code(ctx.author, role=role)

        # send mail
        await self._send_verification_email(ctx.author, email, code)
        await ctx.send("podívej se do mailu ^.^")

    @commands.check(check.is_not_verified)
    @commands.cooldown(rate=5, per=120, type=commands.BucketType.user)
    @commands.command(hidden=True)
    async def reverify(self, ctx):
        """Ask for verification code"""
        # TODO
        pass

    @commands.check(check.is_in_jail)
    @commands.check(check.is_not_verified)
    @commands.cooldown(rate=3, per=120, type=commands.BucketType.user)
    @commands.command()
    async def submit(self, ctx, code: str):
        """Submit verification code"""
        db_user = repo_u.get(ctx.author.id)
        if db_user is None:
            raise exceptions.NotInDatabase()

        if db_user.status != "pending":
            raise exceptions.ProblematicVerification(status=db_user.status)

        pass

    ##
    ## Helper functions
    ##
    def _email_to_role(self, email: str) -> discord.Role:
        """Get role from email address"""
        registered = config.get("verification suffixes")
        constraints = config.get("verification constraints")
        username = email.split("@")[0]

        for domain, role_id in registered.items()[:-1]:
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
                raise exceptions.BadEmail(expected=constraint)

        # domain not found, fallback to basic guest role
        constraint = list(constraint.values())[-1]
        match = re.fullmatch(constraint, username)
        # return
        if match is not None:
            return self.getGuild().get_role(role_id)
        else:
            raise exceptions.BadEmail(expected=constraint)

    def _generate_and_save_code(self, member: discord.Member, role: discord.Role) -> str:
        code_source = string.ascii_uppercase.replace("O", "").replace("I", "") + string.digits
        code = "".join(random.choices(code_source, k=8))

        repo_u.save_code(code=code, discord_id=member.id)
        return code

    async def _send_verification_email(self, member: discord.Member, email: str, code: str) -> bool:
        # TODO Move texts somewhere else
        cleartext = """\
            Tvůj verifikační kód pro {guild_name} Discord server je: {code}.
            Ověříš se příkazem ?submit {code}.

            - {bot_name} (hash {git_hash})
        """.format(
            guild_name=self.getGuild().name,
            code=code,
            bot_name=self.bot.name,
            git_hash=utils.git_hash()[:7],
        )

        richtext = """\
            <body style="background-color:{color_bg};margin:0;text-align:center;">
            <div style="background-color:{color_bg};margin:0;padding:20px;text-align:center;">
                <img src="{bot_avatar}" alt="{bot_name}" style="margin:0 auto;border-radius:100%;border:5px solid {color_fg};height:{bot_avatar_size};width:{bot_avatar_size};backtround-color:{color_bg};" />
                <p style="display:block;color:{color_fg};font-family:{font_family};font-size:24px;">
                    <img src="{user_avatar}" alt="" style="height={user_avatar_size};width:{user_avatar_size};top:4px;margin-right:6px;border-radius:100%;border:2px solid {color_fg};display:inline;position:relative;background-color:{color_bg};">
                    <span>{user_name}</span>
                </p>
                <p style="display:block;color:{color_fg};font-family:{font_family};">Tvůj verifikační kód pro <span style="font-weight:bold;">{guild_name}</span> Discord server:</p>
                <p style="color:{color_bg};font-family:monospace;font-size:30px;letter-spacing:6px;font-weight:bold;background-color:{color_fg};display:inline-block;padding:16px 26px;margin:16px 0;border-radius:4px;">{code}</p>
                <p style="color:{color_fg};font-family:{font_family};margin:10px 0;">Můžeš ho použít jako <span style="font-weight:bold;color:{color_bg};padding:5px 10px;font-family:monospace;background-color:{color_fg};border-radius:2px;">?submit {code}</span></p>
                <p style="display:block;color:{color_fg};font-family:{font_family};">
                    <a style="color:{color_fg};text-decoration:none;font-weight:bold;" href="https://github.com/sinus-x/rubbergoddess" target="_blank">{bot_name}</a>
                , hash {git_hash}</p>
            </div>
            </body>
        """.format(
            # styling
            color_bg=config.color,
            color_fg="white",
            font_family="Arial,Verdana,sans-serif",
            # names
            guild_name=self.getGuild().name,
            bot_name=self.bot.user.name,
            user_name=member.name,
            # codes
            code=code,
            git_hash=utils.git_hash()[:7],
            # images
            bot_avatar=self.bot.user.avatar_url_as(static_format="png", size=128),
            bot_avatar_size="120px",
            user_avatar=member.avatar_url_as(static_format="png", size=32),
            user_avatar_size="20px",
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "{guild_name} → {user_name}".format(
            guild_name=self.getGuild().name, user_name=member.name
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
        if not isinstance(error, exceptions.RubbergoddessException):
            return

        if isinstance(error, exceptions.ProblematicVerification):
            await self.output.error("exception", "ProblematicVerification", status=error.status)
            return

        if isinstance(error, exceptions.BadEmail):
            await self.output.error("exception", "BadEmail", constraint=error.constraint)
            return

        if isinstance(error, exceptions.VerificationException):
            await self.output.error("exception", error.__name__)
            return


def setup(bot):
    bot.add_cot(Gatekeeper(bot))
