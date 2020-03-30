import datetime
from sqlalchemy.orm.exc import NoResultFound

import discord
from discord.ext import commands

import utils
from config import config, messages
from config.emotes import Emotes as emote
from logic import convert
from features import verification
from repository import user_repo
from repository.database import database, session
from repository.database.verification import User
from repository.database.year_increment import User_backup

user_r = user_repo.UserRepository()

config = config.Config
messages = messages.Messages
convert = convert.Convert

class FitWide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification = verification.Verification(bot, user_r)

    async def is_admin(ctx):
        return ctx.author.id == config.admin_id

    async def is_mod(ctx):
        guild = ctx.message.guild
        mod = discord.utils.get(guild.roles, name="MOD")
        return mod in ctx.author.roles

    async def is_in_modroom(ctx):
        return ctx.message.channel.id == config.mod_room

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(is_in_modroom)
    @commands.command()
    async def find_rolehoarders(self, ctx, limit=config.rolehoarder_default_limit):
        guild = self.bot.get_guild(config.guild_id)
        members = guild.members

        found_members = []

        for member in members:
            role_count = 0
            for role in member.roles:
                if role.name.lower() in config.subjects:
                    role_count += 1
            if role_count > 0:
                found_members.append((member, role_count))

        msg = ""

        if len(found_members) == 0:
            msg = messages.rolehoarders_none
        else:
            found_members.sort(key=lambda x: x[1], reverse=True)
            for member, role_count in found_members[:limit]:
                line = "{id} - {name} ({num} rolí)\n".format(id=member.id, name=member.name, num=role_count)
                if len(line) + len(msg) >= 2000:
                    await ctx.send(msg)
                    msg = line
                else:
                    msg += line

        await ctx.send(msg)

    @commands.check(is_mod)
    @commands.check(is_in_modroom)
    @commands.command()
    async def offer_subjects(self, ctx, group = None):
        guild = self.bot.get_guild(config.guild_id)
        add_subjects = discord.utils.get(guild.channels, name="add-subjects")

        # when adding everything, delete all previous posts
        deleted = 0
        if not group:
            deleted = len(await add_subjects.purge())

        ctr_ca = 0
        ctr_ch = 0
        for category in guild.categories:
            has_subjects = False
            if not group:
                for c in category.text_channels:
                    if c.name in config.subjects:
                        has_subjects = True
                        break
            if not group and not has_subjects:
                continue

            elif group and category.name.lower() != group.lower():
                continue

            await add_subjects.send("**{}**".format(category.name.upper()))

            ctr_ca += 1
            msg = ""
            i = 0
            for channel in category.text_channels:
                if channel.name not in config.subjects:
                    continue
                if i >= 10:
                    await add_subjects.send(msg)
                    i = 0
                    msg = ""
                msg += "\n{} #{}".format(convert.emote_number_from_int(i), channel.name)
                msg += " **{}**".format(channel.topic) if channel.topic else ""
                i += 1
                ctr_ch += 1
            await add_subjects.send(msg)

        title = config.default_prefix + "offer_subjects result"
        desc = "For: {}".format(ctx.author.name)
        cleared = "Yes, {} post{}".format(deleted, "s" if deleted > 1 else "") if group is None else "No"
        embed = discord.Embed(title=title, description=desc, color=config.color)
        embed.add_field(name="Cleared?", value=cleared, inline=False)
        embed.add_field(name="Groups", value=ctr_ca, inline=True)
        embed.add_field(name="Subjects", value=ctr_ch, inline=True)
        await ctx.send(embed=embed)

        return

    @commands.check(is_mod)
    @commands.command()
    async def purge(self, ctx, channel, limit = None, pinMode = None):
        #TODO Add user argument
        guild = self.bot.get_guild(config.guild_id)
        ch = discord.utils.get(guild.text_channels, name=channel.replace("#", ""))
        log = discord.utils.get(guild.text_channels, id=config.log_channel)
        pin = False
        deleted = 0

        if limit:
            try:
                limit = int(limit) + 1
            except ValueError:
                self.purgeHelp()
        if pinMode:
            pin = True

        if limit:
            msgs = ch.history(limit=limit)
        else:
            msgs = ch.history()
        ctr_del = 0
        ctr_skip = 0
        ctr_err = 0
        async for m in msgs:
            if pin and m.pinned and pinMode == "pinStop":
                break
            elif pin and m.pinned and pinMode == "pinSkip":
                ctr_skip += 1
                continue
            try:
                await m.delete()
                ctr_del += 1
            except discord.HTTPException:
                ctr_err += 1
        desc = "Log entry for " + ctx.author.name
        embed = discord.Embed(title="?purge", description=desc, color=config.color)
        embed.add_field(name="Settings", value="Channel **{}**, limit **{}**, pinMode **{}**".
            format(channel, limit-1 if limit else "none", pinMode if pinMode else "ignore"))
        embed.add_field(name="Result", value="**{}** removed, **{}** skipped. **{}** errors occured.".
            format(ctr_del-1, ctr_skip, ctr_err), inline=False)
        await log.send(embed=embed)


    @purge.error
    async def purgeHelp(self, ctx, error):
        # print embed
        embed = discord.Embed(title="?purge", color=config.color)
        embed.add_field(name="Usage:", value="?purge <channel> [<count>] [pinSkip|pinStop]")
        await ctx.send(embed=embed)


    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(is_admin)
    @commands.command()
    async def role_check(self, ctx, p_verified: bool = True,
                         p_move: bool = True, p_status: bool = True,
                         p_role: bool = True, p_muni: bool = True):
        guild = self.bot.get_guild(config.guild_id)
        members = guild.members

        verify = discord.utils.get(guild.roles, name="Verify")
        host = discord.utils.get(guild.roles, name="Host")
        bot = discord.utils.get(guild.roles, name="Bot")
        poradce = discord.utils.get(guild.roles, name="Poradce")
        dropout = discord.utils.get(guild.roles, name="Dropout")
        muni = discord.utils.get(guild.roles, name="MUNI")

        verified = [member for member in members
                    if verify in member.roles and
                    host not in member.roles and
                    bot not in member.roles and
                    poradce not in member.roles]

        if not p_muni:
            verified = [member for member in verified
                        if muni not in member.roles]

        permited = session.query(Permit)
        permited_ids = [int(person.discord_ID) for person in permited]

        years = ["0BIT", "1BIT", "2BIT", "3BIT", "4BIT+",
                 "0MIT", "1MIT", "2MIT", "3MIT+", "Dropout"]

        year_roles = {year: discord.utils.get(guild.roles, name=year) for year in years}

        for member in verified:
            if member.id not in permited_ids:
                if p_verified:
                    await ctx.send("Nenasel jsem v verified databazi: " +
                                   utils.generate_mention(member.id))
            else:
                try:
                    login = session.query(Permit).\
                        filter(Permit.discord_ID == str(member.id)).one().login

                    person = session.query(Valid_person).\
                        filter(Valid_person.login == login).one()
                except NoResultFound:
                    continue

                if person.status != 0:
                    if p_status:
                        await ctx.send("Status nesedi u: " + login)

                year = self.verification.transform_year(person.year)

                correct_role = discord.utils.get(guild.roles, name=year)

                if year is not None and correct_role not in member.roles:
                    if p_move:
                        for role_name, role in year_roles.items():
                            if role in member.roles:
                                await member.add_roles(correct_role)
                                await member.remove_roles(role)
                                await ctx.send("Presouvam: " + member.display_name +
                                               " z " + role_name + " do " + year)
                                break
                        else:
                            await member.add_roles(dropout)
                            await ctx.send("Presouvam: " + member.display_name +
                                           " z " + role_name + " do dropout")
                    elif p_role:
                        await ctx.send("Nesedi mi role u: " +
                                       utils.generate_mention(member.id) +
                                       ", mel by mit roli: " + year)
                elif year is None:
                    if p_move:
                        for role_name, role in year_roles.items():
                            if role in member.roles:
                                await member.add_roles(dropout)
                                await member.remove_roles(role)
                                await ctx.send("Presouvam: " + member.display_name +
                                               " z " + role_name + " do dropout")
                                break
                        else:
                            await member.add_roles(dropout)
                            await ctx.send("Presouvam: " + member.display_name +
                                           " z " + role_name + " do dropout")
                    elif p_role:
                        await ctx.send("Nesedi mi role u: " +
                                       utils.generate_mention(member.id) +
                                       ", ma ted rocnik: " + person.year)

        await ctx.send("Done")

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(is_admin)
    @commands.command()
    async def increment_roles(self, ctx):
        database.base.metadata.create_all(database.db)

        guild = self.bot.get_guild(config.guild_id)

        BIT_names = [str(x) + "BIT" + ("+" if x == 4 else "")
                     for x in range(5)]
        BIT = [discord.utils.get(guild.roles, name=role_name)
               for role_name in BIT_names]

        MIT_names = [str(x) + "MIT" + ("+" if x == 3 else "")
                     for x in range(4)]
        MIT = [discord.utils.get(guild.roles, name=role_name)
               for role_name in MIT_names]

        # pridat kazdeho 3BIT a 2MIT cloveka do DB pred tim nez je jebnem do
        # 4BIT+ respektive 3MIT+ role kvuli rollbacku
        session.query(User_backup).delete()

        for member in BIT[3].members:
            session.add(User_backup(member_ID=member.id))
        for member in MIT[2].members:
            session.add(User_backup(member_ID=member.id))

        session.commit()

        for member in BIT[3].members:
            await member.add_roles(BIT[4])
        for member in MIT[2].members:
            await member.add_roles(MIT[3])

        BIT_colors = [role.color for role in BIT]
        await BIT[3].delete()
        await BIT[2].edit(name="3BIT", color=BIT_colors[3])
        await BIT[1].edit(name="2BIT", color=BIT_colors[2])
        await BIT[0].edit(name="1BIT", color=BIT_colors[1])
        bit0 = await guild.create_role(name='0BIT', color=BIT_colors[0])
        await bit0.edit(position=BIT[0].position - 1)

        MIT_colors = [role.color for role in MIT]
        await MIT[2].delete()
        await MIT[1].edit(name="2MIT", color=MIT_colors[2])
        await MIT[0].edit(name="1MIT", color=MIT_colors[1])
        mit0 = await guild.create_role(name='0MIT', color=MIT_colors[0])
        await mit0.edit(position=MIT[0].position - 1)

        general_names = [str(x) + "bit-general" for x in range(4)]
        terminy_names = [str(x) + "bit-terminy" for x in range(1, 3)]
        general_channels = [discord.utils.get(guild.channels,
                                              name=channel_name)
                            for channel_name in general_names]
        terminy_channels = [discord.utils.get(guild.channels,
                                              name=channel_name)
                            for channel_name in terminy_names]
        # TODO: do smth about 4bit general next year, delete it in the meantime
        bit4_general = discord.utils.get(guild.channels, name="4bit-general")
        if bit4_general is not None:
            await bit4_general.delete()

        # move names
        await general_channels[3].edit(name="4bit-general")
        await general_channels[2].edit(name="3bit-general")
        await general_channels[1].edit(name="2bit-general")
        await general_channels[0].edit(name="1bit-general")
        # create 0bit-general
        overwrites = {
            guild.default_role:
                discord.PermissionOverwrite(read_messages=False),
            discord.utils.get(guild.roles, name="0BIT"):
                discord.PermissionOverwrite(read_messages=True,
                                            send_messages=True)
        }
        await guild.create_text_channel(
                '0bit-general', overwrites=overwrites,
                category=general_channels[0].category,
                position=general_channels[0].position - 1
        )

        # delete 3bit-terminy
        await discord.utils.get(guild.channels, name="3bit-terminy").delete()

        await terminy_channels[1].edit(name="3bit-terminy")
        await terminy_channels[0].edit(name="2bit-terminy")
        # create 1bit-terminy
        overwrites = {
            guild.default_role:
                discord.PermissionOverwrite(read_messages=False),
            discord.utils.get(guild.roles, name="1BIT"):
                discord.PermissionOverwrite(read_messages=True,
                                            send_messages=False)
        }
        await guild.create_text_channel(
                '1bit-terminy', overwrites=overwrites,
                category=terminy_channels[0].category,
                position=terminy_channels[0].position - 1
        )

        # give 4bit perms to the new 3bit terminy
        await terminy_channels[1].set_permissions(
            discord.utils.get(guild.roles, name="4BIT+"),
            read_messages=True, send_messages=False
        )

        # Give people the correct mandatory classes after increment
        semester_names = [str(x) + ". Semestr" for x in range(1, 6)]
        semester = [discord.utils.get(guild.categories, name=semester_name)
                    for semester_name in semester_names]
        await semester[0].set_permissions(discord.utils.get(guild.roles,
                                                            name="1BIT"),
                                          read_messages=True,
                                          send_messages=True)
        await semester[0].set_permissions(discord.utils.get(guild.roles,
                                                            name="2BIT"),
                                          overwrite=None)
        await semester[1].set_permissions(discord.utils.get(guild.roles,
                                                            name="1BIT"),
                                          read_messages=True,
                                          send_messages=True)
        await semester[1].set_permissions(discord.utils.get(guild.roles,
                                                            name="2BIT"),
                                          overwrite=None)
        await semester[2].set_permissions(discord.utils.get(guild.roles,
                                                            name="2BIT"),
                                          read_messages=True,
                                          send_messages=True)
        await semester[2].set_permissions(discord.utils.get(guild.roles,
                                                            name="3BIT"),
                                          overwrite=None)
        await semester[3].set_permissions(discord.utils.get(guild.roles,
                                                            name="2BIT"),
                                          read_messages=True,
                                          send_messages=True)
        await semester[3].set_permissions(discord.utils.get(guild.roles,
                                                            name="3BIT"),
                                          overwrite=None)
        await semester[4].set_permissions(discord.utils.get(guild.roles,
                                                            name="3BIT"),
                                          read_messages=True,
                                          send_messages=True)

        await ctx.send('Holy fuck, vsechno se povedlo, '
                       'tak zase za rok ' + emote.wave)

    # TODO: the opposite of increment_roles (for rollback and testing)
    # and role_check to check if peoples roles match the database

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(is_in_modroom)
    @commands.command()
    async def get_users_login(self, ctx, member: discord.Member):
        result = session.query(Permit).\
            filter(Permit.discord_ID == str(member.id)).one_or_none()

        if result is None:
            await ctx.send("Neni v DB prej")
            return
        
        person = session.query(Valid_person).\
            filter(Valid_person.login == result.login).one_or_none()

        if person is None:
            await ctx.send(result.login)
            return

        await ctx.send(("Login: `{p.login}`\nJmeno: `{p.name}`\n"
                        "Rocnik: `{p.year}`").format(p=person))
        
    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(is_in_modroom)
    @commands.command()
    async def get_logins_user(self, ctx, login):
        result = session.query(Permit).\
            filter(Permit.login == login).one_or_none()

        if result is None:
            await ctx.send("Neni na serveru prej")
        else:
            await ctx.send(utils.generate_mention(result.discord_ID))

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(is_in_modroom)
    @commands.command()
    async def reset_login(self, ctx, login):

        result = session.query(Valid_person).\
            filter(Valid_person.login == login).one_or_none()
        if result is None:
            await ctx.send("Neni validni login pre")
        else:
            session.query(Permit).\
                filter(Permit.login == login).delete()
            result.status = 1
            session.commit()
            await ctx.send("Done")

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(is_in_modroom)
    @commands.command()
    async def connect_login_to_user(self, ctx, login, member: discord.Member):

        result = session.query(Valid_person).\
            filter(Valid_person.login == login).one_or_none()
        if result is None:
            await ctx.send("Neni validni login prej")
        else:
            session.add(Permit(login=login, discord_ID=str(member.id)))
            result.status = 0
            session.commit()
            await ctx.send("Done")

    @get_users_login.error
    @reset_login.error
    @get_logins_user.error
    @role_check.error
    @increment_roles.error
    @offer_subjects.error
    async def fitwide_checks_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Nothing to see here comrade. ' + emote.ok)

def setup(bot):
    bot.add_cog(FitWide(bot))
