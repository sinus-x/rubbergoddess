import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string

import discord
from discord import Member
from discord.ext.commands import Bot

import utils
from config.config import Config as config
from config.messages import Messages as messages
from config.emotes import Emotes as emote
from features.base_feature import BaseFeature
from repository.user_repo import UserRepository


class Verification(BaseFeature):
    def __init__(self, bot: Bot, user_repository: UserRepository):
        super().__init__(bot)
        self.repo = user_repository

    def send_mail(self, author, receiver_email, code):
        user_name = author.name
        user_img = author.avatar_url_as(static_format='jpg', size=32)
        h = utils.git_hash()[:7]
        cleartext = """\
Tvůj verifikační kód pro VUT FEKT Discord server je: {code}.
- Rubbergoddess (hash {h})
""".format(code=code, h=h)
        richtext = """\
<body style="background-color:#54355F;margin:0;text-align:center;">
<div style="background-color:#54355F;margin:0;padding:20px;text-align:center;">
    <img src="https://cdn.discordapp.com/avatars/673134999402184734/d61a5db0c50470804b3980567da3a1a0.png?size=128" alt="Rubbergoddess" style="margin:0 auto;border-radius:100%;border:5px solid white;">
    <p style="display:block;color:white;font-family:Arial,Verdana,sans-serif;font-size:24px;">
        <img src="{user_img}" alt="" style="height:20px;width:20px;top:4px;margin-right:6px;border-radius:100%;border:2px solid white;display:inline;position:relative;"><span>{user_name}</span>
    </p>
    <p style="display:block;color:white;font-family:Arial,Verdana,sans-serif;">Tvůj verifikační kód pro <span style="font-weight:bold;">VUT FEKT</span> Discord server:</p>
    <p style="color:#45355F;font-family:monospace;font-size:30px;letter-spacing:6px;font-weight:bold;background-color:white;display:inline-block;padding:16px 26px;margin:16px 0;border-radius:4px;">{code}</p>
    <p style="color:white;font-family:Arial,Verdana,sans-serif;margin:10px 0;">Můžeš ho použít jako <span style="font-weight:bold;color:#45355F;padding:5px 10px;font-family:monospace;background-color:white;border-radius:2px;">?submit {code}</span></p>
    <p style="display:block;color:white;font-family:Arial,Verdana,sans-serif;"><a style="color:white;text-decoration:none;font-weight:bold;" href="https://github.com/sinus-x/rubbergoddess" target="_blank">Rubbergoddess</a>, hash {h}</p>
</div>
</body>""".format(code=code, h=h, user_img=user_img, user_name=user_name)


        msg = MIMEMultipart('alternative')
        #FIXME can this be abused?
        msg['Subject'] = "VUT FEKT verify → {}".format(user_name)
        msg['From'] = config.email_addr
        msg['To'] = receiver_email
        msg['Bcc'] = config.email_addr
        msg.attach(MIMEText(cleartext, 'plain'))
        msg.attach(MIMEText(richtext, 'html'))

        with smtplib.SMTP(config.email_smtp_server, config.email_smtp_port) as server:
            server.starttls()
            server.ehlo()
            server.login(config.email_addr, config.email_pass)
            server.send_message(msg)

    async def has_role(self, user, role_name):
        if type(user) == Member:
            return utils.has_role(user, role_name)
        else:
            guild = await self.bot.fetch_guild(config.guild_id)
            member = await guild.fetch_member(user.id)
            return utils.has_role(member, role_name)

    async def gen_code_and_send_mail(self, message, email, group = None):
        # generate code
        code = ''.join(random.choices(string.ascii_uppercase.replace("O","") + string.digits, k=8))
        # send mail
        self.send_mail(message.author, email, code)
        # save the newly generated code into the database
        self.repo.save_code(code=code, discord_id=str(message.author.id))
        # print approving answer
        domain = email.split("@")[1]
        c = "?verify "
        if group and group in ["FEKT", "VUT"]:
            c += group + "** [redacted]**"
        else:
            c += "**[redacted]**@"+domain
        identifier = "xlogin00" if email.endswith("vutbr.cz") else "e-mail"
        await message.channel.send(
            utils.fill_message(
                "verify_send_success", user=message.author.id, command=c, id=identifier),
            delete_after=config.delay_verify
        )

    async def send_code(self, message):
        # get variables
        args = str(message.content).split(" ")
        login = None
        group = None
        if len(args) == 2:
            login = args[1]
        elif len(args) == 3:
            group = args[1]
            login = args[2]
        else:
            await message.channel.send(
                messages.verify_send_format,
                delete_after=config.delay_verify)
            return

        # check if the user doesn't have the verify role
        if await self.has_role(message.author, config.verification_role):
            await message.channel.send(
                utils.fill_message(
                    "verify_already_verified_role",
                    user=message.author.id,
                    admin=config.admin_id))
        else:
            guild = self.bot.get_guild(config.guild_id)
            jail_info = discord.utils.get(guild.channels, name="jail-info")
            errmsg = None
            if login == "e-mail" or login == "xlogin00":
                await message.channel.send(utils.fill_message("verify_wrong_arguments",
                    user=message.author.id,
                    login=login,
                    emote=emote.facepalm,
                    channel=jail_info.mention),
                    delete_after=config.delay_verify)
                try:
                    await message.delete()
                except discord.HTTPException:
                    return
                return

            # unknown - pending - verified - kicked - banned
            errmsg = None
            u = self.repo.get_user(login=login, discord_id=str(message.author.id))

            if u is None or u and u.status == "unknown":
                # send verify message
                if group and group.upper() == "FEKT":
                    email = "{}@stud.feec.vutbr.cz".format(login)
                elif group and group.upper() == "VUT":
                    email = "{}@vutbr.cz".format(login)
                else:
                    if "@" not in login:
                        await message.channel.send(utils.fill_message("verify_wrong_arguments",
                            user=message.author.id, emote=emote.facepalm, 
                            channel=jail_info.mention))
                        return
                    email = login
                    if login.endswith("stud.feec.vutbr.cz"):
                        group = "FEKT"
                    elif login.endswith("@feec.vutbr.cz"):
                        group = "FEKT"
                        email = email.replace("@feec", "@stud.feec")
                    elif login.endswith("vutbr.cz"):
                        group = "VUT"
                    elif login.endswith("muni.cz"):
                        group = "MUNI"
                    elif login.endswith("cuni.cz"):
                        group = "CUNI"
                    elif login.endswith("cvut.cz"):
                        group = "ČVUT"
                    elif login.endswith("vsb.cz"):
                        group = "VŠB"
                    else:
                        group = "GUEST"
                self.repo.add_user(login, group.upper(), status="pending", discord_id=str(message.author.id))
                await self.gen_code_and_send_mail(message, email, group=group)

            elif u.status == "pending":
                # say that message has been sent
                await message.channel.send(utils.fill_message(
                    "verify_already_sent", user=message.author.id, admin=config.admin_id),
                    delete_after=config.delay_verify)

            elif u.status == "verified":
                # say that the user is already verified
                #TODO do nothing if not in #jail
                await message.channel.send(
                    utils.fill_message(
                        "verify_already_verified_db",
                        user=message.author.id,
                        admin=config.admin_id))

            elif u.status == "kicked":
                # say that the user has been kicked before
                errmsg = "Pokus o verify s *kicked* záznamem"
                await message.channel.send(utils.fill_message(
                    "verify_send_kicked", user=message.author.id, admin=config.admin_id))

            elif u.status == "banned":
                # say that the user has been banned before
                errmsg = "Pokus o verify s *banned* záznamem"
                await message.channel.send(utils.fill_message(
                    "verify_send_banned", user=message.author.id, admin=config.admin_id))

            else:
                # show help
                await message.channel.send(utils.fill_message(
                    "verify_send_format", user=message.author.id),
                    delete_after=config.delay_verify)

            if errmsg:
                embed = discord.Embed(title=errmsg, color=config.color)
                embed.add_field(name="User", value=utils.generate_mention(message.author.id))
                embed.add_field(name="Message", value=message.content, inline=False)
                channel = self.bot.get_channel(config.log_channel)
                await channel.send(embed=embed)

        try:
            await message.delete()
        except discord.HTTPException:
            return

    async def verify (self, message):
        """Verify user entry in database"""
        # get variables
        if len(str(message.content).split(" ")) != 2:
            await message.channel.send(messages.verify_verify_format)
            return
        code = str(message.content).split(" ")[1]

        # only process users that are not verified
        if not await self.has_role(message.author, config.verification_role):
            guild = self.bot.get_guild(config.guild_id)

            # test for common errors
            errmsg = None
            if code == "kód" or code == "kod":
                await message.channel.send(utils.fill_message("verify_verify_no_code",
                    user=message.author.id, emote=emote.facepalm),
                    delete_after=config.delay_verify)
                return

            new_user = self.repo.get_user(discord_id=str(message.author.id))
            errmsg = None
            if new_user is None:
                await message.channel.send(utils.fill_message(
                    "verify_verify_not_found", user=message.author.id),
                    delete_after=config.delay_verify)
            else:
                # check the verification code
                if code.upper() != new_user.code:
                    await message.channel.send(utils.fill_message(
                        "verify_verify_wrong_code", user=message.author.id),
                        delete_after=config.delay_verify)
                    errmsg = "Neúspěšný pokus o verifikaci kódem"
                else:
                    group = new_user.group

                    if group is None:
                        await message.channel.send(utils.fill_message(
                            "verify_verify_manual", user=message.author.id, admin=config.admin_id))
                        errmsg = "Neúspěšný pokus o verifikaci kódem (chybí skupina)"
                    else:
                        # add verify role
                        guild = self.bot.get_guild(config.guild_id)
                        try:
                            verify = discord.utils.get(message.guild.roles,
                                name=config.verification_role)
                            role = discord.utils.get(message.guild.roles, name=group)
                            member = message.author
                            await message.channel.send(utils.fill_message(
                                "verify_verify_success_public", user=message.author.id,
                                group=group),
                                delete_after=config.delay_verify)
                        except AttributeError:
                            # DM
                            verify = discord.utils.get(guild.roles,
                                name=config.verification_role)
                            role = discord.utils.get(guild.roles, name=group)
                            if not message.author.id:
                                return
                            member = guild.get_member(message.author.id)
                        await member.add_roles(verify)
                        await member.add_roles(role)

                        # save to database
                        self.repo.save_verified(discord_id=str(message.author.id))

                        # text user
                        await member.send(utils.fill_message(
                            "verify_verify_success_private", user=message.author.id))
                        if role.name == "FEKT":
                            await member.send(messages.verify_congrats_fekt)
                        else:
                            await member.send(messages.verify_congrats_guest)
            if errmsg:
                embed = discord.Embed(title=errmsg, color=config.color)
                embed.add_field(name="User", value=utils.generate_mention(message.author.id))
                embed.add_field(name="Message", value=message.content, inline=False)
                channel = self.bot.get_channel(config.log_channel)
                await channel.send(embed=embed)
        try:
            await message.delete()
        except discord.HTTPException:
            return
