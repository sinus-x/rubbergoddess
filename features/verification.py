import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string

import discord
from discord import Member
from discord.ext.commands import Bot

import utils
from config.config import Config
from config.messages import Messages
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
    <p style="color:#45355F;font-family:Arial,Verdana,sans-serif;font-size:30px;letter-spacing:6px;font-weight:bold;background-color:white;display:inline-block;padding:16px 26px;margin:16px 0;border-radius:4px;">{code}</p>
    <p style="display:block;color:white;font-family:Arial,Verdana,sans-serif;"><a style="color:white;text-decoration:none;font-weight:bold;" href="https://github.com/sinus-x/rubbergoddess" target="_blank">Rubbergoddess</a>, hash {h}</p>
</div>
</body>""".format(code=code, h=h, user_img=user_img, user_name=user_name)


        msg = MIMEMultipart('alternative')
        #FIXME can this be abused?
        msg['Subject'] = "VUT FEKT verify → {}".format(user_name)
        msg['From'] = Config.email_addr
        msg['To'] = receiver_email
        msg['Bcc'] = Config.email_addr
        msg.attach(MIMEText(cleartext, 'plain'))
        msg.attach(MIMEText(richtext, 'html'))

        with smtplib.SMTP(Config.email_smtp_server, Config.email_smtp_port) as server:
            server.starttls()
            server.ehlo()
            server.login(Config.email_addr, Config.email_pass)
            server.send_message(msg)

    async def has_role(self, user, role_name):
        if type(user) == Member:
            return utils.has_role(user, role_name)
        else:
            guild = await self.bot.fetch_guild(Config.guild_id)
            member = await guild.fetch_member(user.id)
            return utils.has_role(member, role_name)

    async def gen_code_and_send_mail(self, message, login, mail_postfix):
        # Generate a verification code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        self.send_mail(message.author, login + mail_postfix, code)

        # Save the newly generated code into the database
        self.repo.save_sent_code(login, code)

        await message.channel.send(utils.fill_message("verify_send_success",
                                   user=message.author.id, mail=mail_postfix))

    async def send_code(self, message):
        if len(str(message.content).split(" ")) != 3:
            await message.channel.send(Messages.verify_verify_format)
            return

        # check if the user doesn't have the verify role
        if not await self.has_role(message.author, Config.verification_role):
            almamater = str(message.content).split(" ")[1]
            login = str(message.content).split(" ")[2]

            if login == "xlogin00":
                guild = self.bot.get_guild(Config.guild_id)
                await message.channel.send(utils.fill_message("verify_send_dumbshit",
                    user=message.author.id, emote=emote.facepalm))
                return

            # 0 ... verified
            # 1 ... unverified
            # 2 ... pending
            unsuccessfull = False
            if almamater.upper() == "FEKT":
                if self.repo.get_user(login, status=0) is None and \
                   self.repo.get_user(login, status=2) is None:
                    if self.repo.get_user(login, status=1) is None:
                        self.repo.add_user(login, "FEKT", status=2)
                    await self.gen_code_and_send_mail(message, login, "@stud.feec.vutbr.cz")
                else:
                    unsuccessfull = True
            elif almamater.upper() == "VUT":
                if self.repo.get_user(login, status=0) is None and \
                   self.repo.get_user(login, status=2) is None:
                    if self.repo.get_user(login, status=1) is None:
                        self.repo.add_user(login, "VUT", status=2)
                    await self.gen_code_and_send_mail(message, login, "@vutbr.cz")
                else:
                    unsuccessfull = True
            elif almamater.upper() == "MUNI":
                try:
                    int(login)
                except ValueError:
                    unsuccessfull = True

                if self.repo.get_user(login, status=0) is None and \
                   self.repo.get_user(login, status=2) is None:
                    if self.repo.get_user(login, status=1) is None:
                        self.repo.add_user(login, "MUNI", status=2)
                    await self.gen_code_and_send_mail(message, login, "@mail.muni.cz")
                else:
                    unsuccessfull = True
            else:
                unsuccessfull = True

            if unsuccessfull:
                await message.channel.send(utils.fill_message("verify_send_not_found",
                    user=message.author.id, admin=Config.admin_id))
                embed = discord.Embed(title="Neúspěšný pokus o verify", color=Config.color)
                embed.add_field(name="User", value=utils.generate_mention(message.author.id))
                embed.add_field(name="Message", value=message.content, inline=False)
                channel = self.bot.get_channel(Config.log_channel)
                await channel.send(embed=embed)
        else:
            await message.channel.send(utils.fill_message("verify_already_verified",
                                       user=message.author.id, admin=Config.admin_id))
        try:
            await message.delete()
        except discord.errors.HTTPException:
            return

    #TODO
    @staticmethod
    def transform_year (almamater: str):
        if almamater == "FEKT":
            am = "FEKT"
        elif almamater == "VUT":
            am = "VUT"
        elif len(almamater) == 1:
            if almamater[0] == "MUNI":
                am = "MUNI"
        return am

    async def verify (self, message):
        """"Verify if login is from database"""
        if len(str(message.content).split(" ")) != 3:
            await message.channel.send(Messages.verify_verify_format)
            return

        login = str(message.content).split(" ")[1]
        code = str(message.content).split(" ")[2]

        # Check if the user doesn't have the verify role
        # otherwise they wouldn't need to verify, right?
        if not await self.has_role(message.author, Config.verification_role):
        	# test default input
            if login == "identifikátor":
                guild = self.bot.get_guild(Config.guild_id)
                emote = await guild.fetch_emoji(692103675384037458)
                await message.channel.send(utils.fill_message("verify_send_dumbshit",
                                           user=message.author.id, emote=str(emote)))
                return
            if code == "kód":
                guild = self.bot.get_guild(Config.guild_id)
                await message.channel.send(utils.fill_message(
                	"verify_verify_dumbshit", user=message.author.id, emote=emote.facepalm))
                return

            new_user = self.repo.get_user(login)

            if new_user is not None:
                # check the code
                if code != new_user.code:
                    await message.channel.send(utils.fill_message("verify_verify_wrong_code", user=message.author.id))
                    embed = discord.Embed(title="Neuspesny pokus o verify (kod)", color=0xeee657)
                    embed.add_field(name="User", value=utils.generate_mention(message.author.id))
                    embed.add_field(name="Message", value=message.content, inline=False)
                    channel = self.bot.get_channel(Config.log_channel)
                    await channel.send(embed=embed)
                    return

                # try get the year role
                year = self.transform_year(new_user.year)

                if year is None:
                    await message.channel.send(utils.fill_message(
                        "verify_verify_manual",
                        user=message.author.id,
                        admin=Config.admin_id,
                        year=str(new_user.year)
                        )
                    )

                    embed = discord.Embed(title="Neuspesny pokus o verify (manual)",
                                          color=0xeee657)
                    embed.add_field(name="User", value=utils.generate_mention(message.author.id))
                    embed.add_field(name="Message", value=message.content, inline=False)
                    channel = self.bot.get_channel(Config.log_channel)
                    await channel.send(embed=embed)
                    return

                try:
                    # Get server verify role
                    verify = discord.utils.get(message.guild.roles, name=Config.verification_role)
                    year = discord.utils.get(message.guild.roles, name=year)
                    member = message.author
                except AttributeError:
                    # jsme v PM
                    guild = self.bot.get_guild(Config.guild_id)
                    verify = discord.utils.get(
                        guild.roles,
                        name=Config.verification_role)
                    year = discord.utils.get(guild.roles, name=year)
                    member = guild.get_member(message.author.id)

                await member.add_roles(verify)
                await member.add_roles(year)

                self.repo.save_verified(login, message.author.id)

                await member.send(utils.fill_message("verify_verify_success", user=message.author.id))
                guild = self.bot.get_guild(Config.guild_id)
                fekt = discord.utils.get(guild.roles, name="FEKT")
                if fekt in member.roles:
                    await member.send(Messages.verify_post_verify_fekt)
                else:
                    await member.send(Messages.verify_post_verify_guest)

                if message.channel.type is not discord.ChannelType.private:
                    await message.channel.send(utils.fill_message("verify_verify_success", user=message.author.id))
            else:
                await message.channel.send(utils.fill_message(
                    "verify_verify_not_found", user=message.author.id, admin=Config.admin_id))
                embed = discord.Embed(title="Neuspesny pokus o verify", color=Config.color)
                embed.add_field(name="User", value=utils.generate_mention(message.author.id))
                embed.add_field(name="Message", value=message.content, inline=False)
                channel = self.bot.get_channel(Config.log_channel)
                await channel.send(embed=embed)
        else:
            await message.channel.send(utils.fill_message(
                "verify_already_verified", user=message.author.id, admin=Config.admin_id))

        try:
            await message.delete()
        except discord.errors.Forbidden:
            return
