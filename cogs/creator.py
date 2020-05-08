import re
import csv
import time
import json
import random
import asyncio
import datetime
from operator import itemgetter

import discord
from discord.ext import commands
from discord.colour import Colour

from cogs import errors
from core.config import config
from repository import user_repo
from core import check, rubbercog
from config.messages import Messages as messages

repository = user_repo.UserRepository()


class Creator(rubbercog.Rubbercog):
    """Server building cog"""

    def __init__(self, bot):
        super().__init__(bot)
        self.errors = errors.Errors(bot)
        self.rubbercog = rubbercog.Rubbercog(bot)
        self.creator_running = False
        #self.visible = False

    async def edit_role(self, ctx, guild, role, **kwargs):
        if ctx is not None:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(
                config.channel_guildlog)  # fix to use config
        if guild == self.getGuild() or guild == self.getSlave():
            if role.name.startswith('@'):
                name = role.name.strip('@')
            else:
                name = role.name
            msg = "Editing {} in server {}".format(name, guild.name)
            if 'position' in kwargs:
                position = int(kwargs['position'])
                del kwargs['position']
                msg += " at position {}".format(int(position))
            if config.debug:
                print(msg)
            if position:
                try:
                    await role.edit(server=guild, role=role, position=position)
                except Exception as e:
                    await channel.send("{name} - encountered Error: {error}".format(name=name, error=e))
            try:
                await role.edit(server=guild, role=role, **kwargs)
            except Exception as e:
                await channel.send("{name} - encountered Error: {error}".format(name=name, error=e))
            return
        else:
            await channel.send('Na tomto serveru není možné provést tuto akci')

    async def create_role(self, ctx, guild, **kwargs):
        if ctx is not None:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(
                config.channel_guildlog)  # fix to use config
        if guild == self.getGuild() or guild == self.getSlave():
            position = None
            if 'name' in kwargs:
                name = kwargs['name']
                msg = "Creating {} in server {}".format(name, guild.name)
                if 'position' in kwargs:
                    position = int(kwargs['position'])
                    del kwargs['position']
                    msg += " at position {}".format(int(position))
                if config.debug:
                    print(msg)
                try:
                    await guild.create_role(**kwargs)
                except Exception as e:
                    await channel.send("{name} - encountered Error: {error}".format(name=name, error=e))
                else:
                    if position is not None:
                        try:
                            role = discord.utils.get(guild.roles, name=name)
                            await self.edit_role(ctx, guild, role, position=position)
                        except Exception as e:
                            await channel.send("{name} - encountered Error: {error}".format(name=name, error=e))
            return
        else:
            await channel.send('Na tomto serveru není možné provést tuto akci')

    @commands.group("create")
    @commands.check(check.is_in_modroom)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def creator(self, ctx: commands.Context):
        """Guild building and management cog"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            return

    @creator.command(name="roles")
    async def creator_roles(self, ctx: commands.Context):
        """Create server roles. Takes 2 arguments: 
        1. - guild (master/slave)
        2. - config (optional, for overwriting the config file as well)"""
        self.creator_running = True
        channel = ctx.message.channel
        message = ctx.message
        config_overwrite = False
        args = tuple(re.split(r'\s+', str(message.content).strip("\r\n\t")))
        if len(args) >= 3 and (message.guild == self.getGuild()):
            if args[2].lower() == "master":
                guild = self.getGuild()
            elif args[2].lower() == "slave" and self.getSlave() != 0:
                guild = self.getSlave()
            else:
                await channel.send("Nesplěné požadavky příkazu.")
                return
            if len(args) == 4:
                if args[3].lower() == "config" and config.loader == "docker":
                    config_overwrite = True
                else:
                    # TODO implement for other loaders
                    await channel.send('To pro tenhle loader zatím neumím.')
                    await channel.send('Ignoruji zápis do configu.')

            with open('creator_data/Roles.json', 'rt') as f:
                role_list = json.load(f)

            if config_overwrite:
                with open('config/config.json', 'r') as file:
                    json_object = json.load(file)

            for row in role_list:
                colour = Colour(
                    eval('0x0{}'.format(row["colour"].upper().lstrip("#").lstrip("0x"))))
                permissions = discord.Permissions(row["permissions"])

                if discord.utils.get(guild.roles, name=row["name"]):
                    role = discord.utils.get(guild.roles, name=row["name"])
                    r = [role.name, role.position, role.hoist,
                         role.mentionable, role.permissions, role.colour]
                    a = [row["name"], row["position"], row["hoist"],
                         row["mentionable"], permissions, colour]
                    if a != r:
                        await asyncio.sleep(0.5)
                        await self.edit_role(ctx, guild, role, position=row["position"], hoist=row["hoist"], mentionable=row["mentionable"], permissions=permissions, color=colour)
                else:
                    await asyncio.sleep(0.5)
                    await self.create_role(ctx, guild, name=row["name"], hoist=row["hoist"], mentionable=row["mentionable"], permissions=permissions, color=colour)
                    # API is not a fan of creation and quick edit of roles (can't create one at a position tho)
            if guild == self.getGuild() and config_overwrite:
                for role in guild.roles:
                    name = role.name
                    if name == "MOD":
                        mod_id = discord.utils.get(guild.roles, name=name).id
                        json_object["roles"]["mod_id"] = mod_id
                    elif name == "SUBMOD":
                        submod_id = discord.utils.get(
                            guild.roles, name=name).id
                    elif name == "HELPER":
                        helper_id = discord.utils.get(
                            guild.roles, name=name).id
                    elif name == "VERIFY":
                        json_object["roles"]["verify_id"] = discord.utils.get(
                            guild.roles, name=name).id

                json_object["roles"]["elevated_ids"] = [
                    mod_id, submod_id, helper_id]
                with open('./config/config.json', 'w') as file:
                    json.dump(json_object, file, ensure_ascii=False, indent=4)

            await asyncio.sleep(2)
            self.creator_running = False
            await channel.send('Nastavení rolí dokončeno.')
            return
        else:
            await channel.send("Conditions weren't met or wrong arguments were used")
            return

    @creator.command(name="sync")
    async def creator_sync(self, ctx: commands.Context):
        """Synchronize roles from master to slave."""
        if (ctx.message.guild == self.getGuild()):
            guild = self.getGuild()
            slave = self.getSlave()
            channel = ctx.message.channel
            master_roles = await guild.fetch_roles()

            for role in master_roles:
                slave_role = discord.utils.get(slave.roles, name=role.name)
                if slave_role is not None:
                    r = [role.position, role.hoist, role.mentionable,
                         role.permissions, role.colour]
                    a = [slave_role.position, slave_role.hoist, slave_role.mentionable,
                         slave_role.permissions, slave_role.colour]
                    if a != r:
                        await asyncio.sleep(0.5)
                        await self.edit_role(ctx, slave, slave_role, position=role.position, hoist=role.hoist, mentionable=role.mentionable,
                                             permissions=role.permissions, color=role.colour)
                else:
                    await asyncio.sleep(0.5)
                    await self.create_role(ctx, slave, name=role.name, hoist=role.hoist, mentionable=role.mentionable, permissions=role.permissions, color=role.colour)
                    # API is not a fan of creation and quick edit of roles (can't create one at a position tho)
        await channel.send('Synchronizování rolí dokončeno.')
        return

    @creator.command(name="rolebackup")
    async def creator_role_backup(self, ctx: commands.Context):
        """Backup master server roles."""
        if (ctx.message.guild == self.getGuild()) and config.loader == "docker":
            guild = self.getGuild()
            master_roles = await guild.fetch_roles()
            backup_list = []

            for role in master_roles:
                if role.name == self.bot.user.name:
                    continue
                c = role.color.to_rgb()
                color = "#{:02x}{:02x}{:02x}".format(c[0], c[1], c[2])

                backup_list.append({"position": role.position, "name": role.name,
                                    "colour": color, "hoist": role.hoist, "mentionable": role.mentionable, "permissions": role.permissions.value})

            backup_list = sorted(
                backup_list, key=itemgetter('position'), reverse=True)
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open('./creator_data/Roles_{}.json'.format(now), 'w') as file:
                json.dump(backup_list, file, ensure_ascii=False, indent=4)

            embed = discord.Embed(title="Role backup", color=config.color)
            embed.add_field(
                name="Success", value="Roles were successfully backed up.")
            channel = self.bot.get_channel(config.channel_botlog)
            await channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Role backup", color=config.color)
            embed.add_field(
                name="Fail", value="Writing to files not yet supported for this version")
            channel = self.bot.get_channel(config.channel_botlog)
            await channel.send(embed=embed)
        return

    @creator.command(name="reset")
    async def creator_reset(self, ctx: commands.Context):
        """Delete channels, force reverification"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        return

    @creator.command(name="channels")
    async def creator_channels(self, ctx: commands.Context):
        """Add subject channels"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        return

    @creator.command(name="subjects")
    async def creator_subjects(self, ctx: commands.Context):
        """Send react-to-role messages to #add-subjects"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        return

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        server = role.guild
        if server == self.getGuild() and self.getSlave() != 0:
            guild = self.getSlave()
        else:
            return
        
        await asyncio.sleep(1)

        r = discord.utils.get(guild.roles, name=role.name)
        if r is None:
            await self.create_role(None, guild, name=role.name, hoist=role.hoist, mentionable=role.mentionable, permissions=role.permissions, color=role.colour)
        return

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if self.creator_running == False:
            server = before.guild
            # DO NOT allow changes from more than 1 server, just stick to master-slaves relationship and save your sanity
            if server == self.getGuild() and self.getSlave() != 0:
                guild = self.getSlave()
            else:
                return

            role = None
            now = time.time()
            timeout = 10
            await asyncio.sleep(2)
            while role is None:
                if time.time() > now + timeout:
                    break
                role = discord.utils.get(guild.roles, name=before.name)
            r = [role.name, role.hoist, role.mentionable,
                 role.permissions, role.colour]
            a = [after.name, after.hoist, after.mentionable,
                 after.permissions, after.colour]

            # ignoring positional changes of 1 (otherwise brace for a storm)
            if abs(int(before.position) - int(after.position)) > 1 or a != r:
                await self.edit_role(None, guild, role, name=after.name, position=after.position,
                                     hoist=after.hoist, mentionable=after.mentionable, permissions=after.permissions, color=after.colour)

        return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild == self.getSlave():
            guild = self.getGuild()
            main_member = discord.utils.get(guild.members, id=member.id)
            print(member.roles)
            if main_member is not None:
                for role in main_member.roles:
                    slave_role = discord.utils.get(self.getSlave().roles, name=role.name)
                    if slave_role is not None:
                        for r in member.roles:
                            if r.name == role.name:
                                break
                        else:
                            if config.debug:
                                print("Adding role: "+slave_role.name +
                                      " to "+member.name)
                            try:
                                await member.add_roles(slave_role)
                            except Exception as e:
                                embed = discord.Embed(
                                    title="on_member_update Exception", description="add_roles() failed", color=config.color_error)
                                embed.add_field(name="Role", value=slave_role.name)
                                embed.add_field(name="User", value=member.mention)
                                embed.add_field(name="Exception", value=e)
                                channel = self.bot.get_channel(
                                    config.channel_botlog)
                                await channel.send(embed=embed)

                    else:
                        await config.channel_botlog.send("Role neexistuje")
        return
                
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild == self.getGuild() and self.getSlave() != 0:
            
            slave = self.getSlave()
            slave_member = discord.utils.get(slave.members, id=member.id)
            if slave_member is not None:
                if config.debug:
                    print("Removing member "+slave_member.name)
                try:
                    await slave_member.kick()
                except Exception as e:
                    embed = discord.Embed(
                                title="on_member_remove Exception", description="member.kick() failed", color=config.color_error)
                    embed.add_field(name="User", value=member.mention)
                    embed.add_field(name="Exception", value=e)
                    channel = self.bot.get_channel(
                        config.channel_botlog)
                    await channel.send(embed=embed)
        return

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if guild == self.getGuild() and self.getSlave() != 0:
            server = self.getSlave()
        elif guild == self.getSlave():
            server = self.getGuild()
        else:
            return
        
        await asyncio.sleep(2)

        try:
            banned = await server.fetch_ban(user)
        except discord.errors.NotFound:
            banned = None
        if banned is None:
            if config.debug:
                print("Banning member "+user.name)
            try:
                await server.ban(user)
                #repository.update_status(discord_id=user.id, status="banned")
            except Exception as e:
                embed = discord.Embed(
                            title="on_member_remove Exception", description="member.kick() failed", color=config.color_error)
                embed.add_field(name="User", value=user.mention)
                embed.add_field(name="Exception", value=e)
                channel = self.bot.get_channel(
                    config.channel_botlog)
                await channel.send(embed=embed)
        return

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if guild == self.getGuild() and self.getSlave() != 0:
            server = self.getSlave()
        elif guild == self.getSlave():
            server = self.getGuild()
        else:
            return

        await asyncio.sleep(2)

        try:
            banned = await server.fetch_ban(user)
        except discord.errors.NotFound:
            banned = None
        if banned is not None:
            if config.debug:
                print("Unbanning member "+user.name)
            try:
                await server.unban(user)
                #repository.update_status(discord_id=user.id, status="reverify")
            except Exception as e:
                embed = discord.Embed(
                            title="on_member_remove Exception", description="member.kick() failed", color=config.color_error)
                embed.add_field(name="User", value=user.mention)
                embed.add_field(name="Exception", value=e)
                channel = self.bot.get_channel(
                    config.channel_botlog)
                await channel.send(embed=embed)
        return

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return
        server = before.guild
        if server == self.getGuild() and self.getSlave() != 0:
            guild = self.getSlave()
        else:
            return
        
        await asyncio.sleep(1)
        member = discord.utils.get(guild.members, id=before.id)

        if member is not None:
            after_roles = []
            member_roles = []

            for role in after.roles:
                after_roles.append(role.name)
                slave_role = discord.utils.get(guild.roles, name=role.name)
                if slave_role is not None:
                    for r in member.roles:
                        member_roles.append(r.name)
                        if r.name == role.name:
                            break
                    else:
                        if config.debug:
                            print("Adding role: "+slave_role.name +
                                  " to "+member.name)
                        try:
                            await member.add_roles(slave_role)
                        except Exception as e:
                            embed = discord.Embed(
                                title="on_member_update Exception", description="add_roles() failed", color=config.color_error)
                            embed.add_field(name="Role", value=slave_role.name)
                            embed.add_field(name="User", value=member.mention)
                            embed.add_field(name="Exception", value=e)
                            channel = self.bot.get_channel(
                                config.channel_botlog)
                            await channel.send(embed=embed)

                else:
                    await config.channel_botlog.send("Role neexistuje")

            for name in member_roles:
                if name not in after_roles:
                    role = discord.utils.get(guild.roles, name=name)
                    if config.debug:
                        print("Removing role: "+role.name+" from "+member.name)
                    try:
                        await member.remove_roles(role)
                    except Exception as e:
                        embed = discord.Embed(
                            title="on_member_update Exception", description="remove_roles() failed", color=config.color_error)
                        embed.add_field(name="Role", value=role.name)
                        embed.add_field(name="User", value=member.mention)
                        embed.add_field(name="Exception", value=e)
                        channel = self.bot.get_channel(config.channel_botlog)
                        await channel.send(embed=embed)

        return

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        server = role.guild
        if server == self.getGuild() and self.getSlave() != 0:
            guild = self.getSlave()
        else:
            return
        
        await asyncio.sleep(1)
        role = discord.utils.get(guild.roles, name=role.name)
        if role is not None:
            print("Deleting role {} at {}".format(role.name, guild.name))

            try:
                await role.delete()
            except Exception as e:
                embed = discord.Embed(title="on_guild_role_delete Exception",
                                      description="role.delete() failed", color=config.color_error)
                embed.add_field(name="Role", value=role.name)
                embed.add_field(name="Exception", value=e)
                channel = self.bot.get_channel(config.channel_botlog)
                await channel.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(Creator(bot))
