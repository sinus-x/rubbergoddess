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
        # self.visible = False

    def isRunning(self):
        return self.creator_running

    async def edit_role(self, ctx, guild, role, **kwargs):
        if ctx is not None:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(config.channel_guildlog)
        if guild == self.getGuild() or guild == self.getSlave():
            if role.name.startswith("@"):
                name = role.name.strip("@")
            else:
                name = role.name
            msg = "Editing {} in server {}".format(name, guild.name)
            if "position" in kwargs:
                position = int(kwargs["position"])
                del kwargs["position"]
                msg += " at position {}".format(int(position))
            if config.debug:
                print(msg)
            if position:
                try:
                    await role.edit(server=guild, role=role, position=position)
                except Exception as e:
                    await channel.send(
                        "{name} - encountered Error: {error}".format(name=name, error=e)
                    )
            try:
                await role.edit(server=guild, role=role, **kwargs)
            except Exception as e:
                await channel.send("{name} - encountered Error: {error}".format(name=name, error=e))
            return
        else:
            await channel.send("Na tomto serveru není možné provést tuto akci")

    async def create_role(self, ctx, guild, **kwargs):
        if ctx is not None:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(config.channel_guildlog)
        if guild == self.getGuild() or guild == self.getSlave():
            position = None
            if "name" in kwargs:
                name = kwargs["name"]
                if config.debug:
                    msg = "Creating {} in server {}".format(name, guild.name)
                if "position" in kwargs:
                    position = int(kwargs["position"])
                    del kwargs["position"]
                    msg += " at position {}".format(int(position))
                if config.debug:
                    print(msg)
                try:
                    await guild.create_role(**kwargs)
                except Exception as e:
                    await channel.send(
                        "{name} - encountered Error: {error}".format(name=name, error=e)
                    )
                else:
                    if position is not None:
                        try:
                            role = discord.utils.get(guild.roles, name=name)
                            await self.edit_role(ctx, guild, role, position=position)
                        except Exception as e:
                            await channel.send(
                                "{name} - encountered Error: {error}".format(name=name, error=e)
                            )
            return
        else:
            await channel.send("Na tomto serveru není možné provést tuto akci")

    async def create_channel(self, ctx, guild, channel_type, name, **kwargs):
        """channel_type can be: category / text / voice"""
        if guild == self.getGuild() or guild == self.getSlave():
            position = None

            if config.debug:
                print("Creating channel {} in server {}".format(name, guild.name))
            if channel_type == "category":
                try:
                    await guild.create_category(name, **kwargs)
                except Exception as e:
                    await ctx.channel.send(
                        "create_category() {name} encountered Error: {error}".format(
                            name=name, error=e
                        )
                    )
            elif channel_type == "text":
                try:
                    await guild.create_text_channel(name, **kwargs)
                except Exception as e:
                    await ctx.channel.send(
                        "create_text_channel() {name} encountered Error: {error}".format(
                            name=name, error=e
                        )
                    )
            elif channel_type == "voice":
                try:
                    await guild.create_voice_channel(name, **kwargs)
                except Exception as e:
                    await ctx.channel.send(
                        "create_voice_channel() {name} encountered Error: {error}".format(
                            name=name, error=e
                        )
                    )

        else:
            await ctx.channel.send("Na tomto serveru není možné provést tuto akci")
        return

    async def edit_channel(self, ctx, guild, channel, kwargs):
        if guild == self.getGuild() or guild == self.getSlave():
            if config.debug:
                print("Editing channel {} in server {}".format(channel.name, guild.name))
            try:
                await channel.edit(**kwargs)
            except Exception as e:
                await ctx.channel.send(
                    "channel.edit() {name} encountered Error: {error}".format(
                        name=channel.name, error=e
                    )
                )

        else:
            await ctx.channel.send("Na tomto serveru není možné provést tuto akci")
        return

    @commands.group("create")
    @commands.check(check.is_mod)
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
        args = tuple(re.split(r"\s+", str(message.content).strip("\r\n\t")))
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
                    await channel.send("To pro tenhle loader zatím neumím.")
                    await channel.send("Ignoruji zápis do configu.")

            with open("creator_data/Roles.json", "rt") as f:
                role_list = json.load(f)

            if config_overwrite:
                with open("config/config.json", "r") as file:
                    json_object = json.load(file)

            for row in role_list:
                colour = Colour(
                    eval("0x0{}".format(row["colour"].upper().lstrip("#").lstrip("0x")))
                )
                permissions = discord.Permissions(row["permissions"])

                if discord.utils.get(guild.roles, name=row["name"]):
                    role = discord.utils.get(guild.roles, name=row["name"])
                    r = [
                        role.name,
                        role.position,
                        role.hoist,
                        role.mentionable,
                        role.permissions,
                        role.colour,
                    ]
                    a = [
                        row["name"],
                        row["position"],
                        row["hoist"],
                        row["mentionable"],
                        permissions,
                        colour,
                    ]
                    if a != r:
                        await asyncio.sleep(0.5)
                        await self.edit_role(
                            ctx,
                            guild,
                            role,
                            position=row["position"],
                            hoist=row["hoist"],
                            mentionable=row["mentionable"],
                            permissions=permissions,
                            color=colour,
                        )
                else:
                    await asyncio.sleep(0.5)
                    await self.create_role(
                        ctx,
                        guild,
                        name=row["name"],
                        hoist=row["hoist"],
                        mentionable=row["mentionable"],
                        permissions=permissions,
                        color=colour,
                    )
                    # API is not a fan of creation and quick edit of roles (can't create one at a position tho)
            if guild == self.getGuild() and config_overwrite:
                for role in guild.roles:
                    name = role.name
                    if name == "MOD":
                        mod_id = discord.utils.get(guild.roles, name=name).id
                        json_object["roles"]["mod_id"] = mod_id
                    elif name == "SUBMOD":
                        submod_id = discord.utils.get(guild.roles, name=name).id
                    elif name == "HELPER":
                        helper_id = discord.utils.get(guild.roles, name=name).id
                    elif name == "VERIFY":
                        json_object["roles"]["verify_id"] = discord.utils.get(
                            guild.roles, name=name
                        ).id

                json_object["roles"]["elevated_ids"] = [mod_id, submod_id, helper_id]
                with open("./config/config.json", "w") as file:
                    json.dump(json_object, file, ensure_ascii=False, indent=4)

            await asyncio.sleep(2)
            self.creator_running = False
            await channel.send("Nastavení rolí dokončeno.")
            return
        else:
            await channel.send("Conditions weren't met or wrong arguments were used")
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

                backup_list.append(
                    {
                        "position": role.position,
                        "name": role.name,
                        "colour": color,
                        "hoist": role.hoist,
                        "mentionable": role.mentionable,
                        "permissions": role.permissions.value,
                    }
                )

            backup_list = sorted(backup_list, key=itemgetter("position"), reverse=True)
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open("./creator_data/Roles_{}.json".format(now), "w") as file:
                json.dump(backup_list, file, ensure_ascii=False, indent=4)

            embed = discord.Embed(title="Role backup", color=config.color)
            embed.add_field(name="Success", value="Roles were successfully backed up.")
            channel = self.bot.get_channel(config.channel_botlog)
            await channel.send(embed=embed)
        else:
            embed = discord.Embed(title="Role backup", color=config.color)
            embed.add_field(
                name="Fail", value="Writing to files not yet supported for this version"
            )
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
        """Create server channels"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        return

    @creator.command(name="subjects")
    async def creator_subjects(self, ctx: commands.Context):
        """Send react-to-role messages to #add-subjects"""
        await self.throwNotification(ctx, messages.err_not_implemented)
        return


def setup(bot):
    bot.add_cog(Creator(bot))
