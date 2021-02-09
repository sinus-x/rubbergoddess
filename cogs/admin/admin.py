import asyncio
import subprocess

from discord.ext import commands, tasks

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from core.config import config


class Admin(rubbercog.Rubbercog):
    """Rubbergoddess administration"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("admin")
        self.text = CogText("admin")

        self.usage = {}

        self.jail_check.start()
        self.just_booted = True

    def cog_unload(self):
        self.jail_check.cancel()

    ##
    ## Commands
    ##

    @commands.check(acl.check)
    @commands.group(name="system")
    async def system(self, ctx):
        """Prepare the guild for shutdown"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

    @commands.check(acl.check)
    @system.command(name="off", aliases=["down"])
    async def system_off(self, ctx, *, reason: str = None):
        """Prepare for power off

        reason: Optional. The reason for shutdown
        """
        if reason is None:
            reason = ""
        else:
            reason = " " + self.text.get("system_off", "reason", reason=reason)

        jail = self.getGuild().get_channel(config.get("channels", "jail"))
        everyone = self.getGuild().default_role
        botspam = self.getGuild().get_channel(config.get("channels", "botspam"))

        visited = []

        if jail is not None:
            # send message
            await jail.send(self.text.get("system_off", "jail") + reason)
            # switch to read-only
            await jail.set_permissions(everyone, send_messages=False, reason="?system off")
            visited.append(jail.mention)

        if botspam is not None:
            # send message
            await botspam.send(self.text.get("system_off", "botspam") + reason)
            visited.append(botspam.mention)

        # send confirmation message
        if len(visited) > 0:
            await ctx.send(self.text.get("system_off", "ok", channels=", ".join(visited)))
        else:
            await ctx.send(self.text.get("system_fail"))
        await self.event.sudo(ctx, "System off" + f": {reason}." if len(reason) else ".")

    @commands.check(acl.check)
    @system.command(name="on", aliases=["up"])
    async def system_on(self, ctx):
        """Restore"""
        jail = self.getGuild().get_channel(config.get("channels", "jail"))
        everyone = self.getGuild().default_role
        botspam = self.getGuild().get_channel(config.get("channels", "botspam"))

        visited = []

        if jail is not None:
            # remove the message
            messages = await jail.history(limit=10).flatten()
            for message in messages:
                if message.content.startswith(self.text.get("system_off", "jail")):
                    await message.delete()
                    break
            # switch to read-write
            await jail.set_permissions(everyone, send_messages=True, reason="?system on")
            visited.append(jail.mention)

        if botspam is not None:
            # send message
            await botspam.send(self.text.get("system_on", "botspam"))
            visited.append(botspam.mention)

        # send confirmation message
        if len(visited) > 0:
            await ctx.send(self.text.get("system_on", "ok", channels=", ".join(visited)))
        else:
            await ctx.send(self.text.get("power_fail"))
        await self.event.sudo(ctx, "System on.")

    @commands.check(acl.check)
    @system.command(name="shutdown")
    async def system_shutdown(self, ctx):
        """Shutdown the bot"""
        await self.event.sudo(ctx, "System shutdown.")
        await self.console.critical(ctx, "System shutdown initiated.")
        await self.bot.logout()

    @commands.check(acl.check)
    @commands.command(name="status")
    async def status(self, ctx: commands.Context):
        """Display systemd status"""
        if config.loader != "systemd":
            return await ctx.send(self.text.get("systemd_only"))

        stdout = None
        try:
            stdout = subprocess.check_output(
                "sudo systemctl status rubbergoddess", shell=True
            ).decode("utf-8")
        except subprocess.CalledProcessError as e:
            await self.console.error(ctx, "No access to systemctl", e)
            await self.output.error(ctx, "No access to systemctl", e)
            return

        await ctx.send("```\n{}\n```".format(stdout))

    @commands.check(acl.check)
    @commands.command(name="journalctl")
    async def journalctl(self, ctx: commands.Context):
        """See bot logs"""
        cmd = None
        result = None

        if config.loader == "standalone":
            result = await self._readFile(ctx, "rubbergoddess.log")
        elif config.loader == "systemd":
            cmd = "sudo journalctl -u rubbergoddess"
            try:
                result = subprocess.check_output(cmd + " | tail -n 40", shell=True).decode("utf-8")
            except subprocess.CalledProcessError as e:
                await self.output.error(ctx, "Subprocess error", e)
                return

        output = list(result[0 + i : 1960 + i] for i in range(0, len(result), 1960))
        for o in output:
            await ctx.send("```{}```".format(o))
        await utils.delete(ctx)

    @commands.check(acl.check)
    @commands.command()
    async def config(self, ctx):
        """See configuration from 'bot' section"""
        embed = self.embed(ctx=ctx)

        # fmt: off
        # hosting
        embed.add_field(
            name=self.text.get("config_embed", "host"),
            value=config.get("bot", "host")
        )
        embed.add_field(
            name=self.text.get("config_embed", "loader"),
            value=config.get("bot", "loader")
        )
        # logging
        embed.add_field(
            name=self.text.get("config_embed", "log_level"),
            value=config.get("bot", "logging")
        )
        # extensions
        embed.add_field(
            name=self.text.get("config_embed", "default_cogs"),
            value=", ".join([
                x.lower()
                for x
                in sorted(config.get("bot", "extensions").append("errors"))
            ]),
            inline=False,
        )
        embed.add_field(
            name=self.text.get("config_embed", "loaded_cogs"),
            value=", ".join([x.lower() for x in sorted(self.bot.cogs.keys())]),
            inline=False,
        )
        # fmt: on

        await ctx.send(embed=embed)
        await utils.delete(ctx)

    @commands.cooldown(rate=2, per=20, type=commands.BucketType.channel)
    @commands.check(acl.check)
    @commands.command(name="commands")
    async def command_stats(self, ctx):
        """Command invocation statistics"""
        embed = self.embed(
            ctx=ctx,
            title=self.text.get("stats", "title"),
            description=self.text.get("stats", "description"),
        )

        num = self.config.get("limit")
        if len(self.usage) < num:
            num = len(self.usage)
        embed.add_field(
            name=self.text.get("stats", "top_0", num=num),
            value=self.getCommandsStats(0),
            inline=False,
        )

        message = await ctx.send(embed=embed)
        await message.add_reaction("⏪")
        await message.add_reaction("◀")
        await message.add_reaction("▶")

        await utils.room_check(ctx)

    ##
    ## Logic
    ##

    @tasks.loop(minutes=10)
    async def jail_check(self):
        """Check if the #jail is writable. This is used if the bot admin
        forgets about that fact they did not run `system on` after the bot
        loaded."""

        if self.just_booted:
            self.just_booted = False
            return

        async def get_jail_message():
            jail = self.getGuild().get_channel(config.get("channels", "jail"))
            if jail is not None:
                for message in await jail.history(limit=10).flatten():
                    if message.content.startswith(self.text.get("system_off", "jail")):
                        return message

        if await get_jail_message() is None:
            return

        botspam = self.getGuild().get_channel(config.get("channels", "botspam"))
        await botspam.send(self.text.get("system_check", admin_id=config.admin_id))

    @jail_check.before_loop
    async def before_jail_check(self):
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if not hasattr(ctx, "command") or not hasattr(ctx.command, "qualified_name"):
            return

        name = ctx.command.qualified_name
        if name in self.usage:
            self.usage[name] += 1
        else:
            self.usage[name] = 1

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """command_stats scrolling"""
        if str(reaction) not in ("⏪", "◀", "▶"):
            return

        if user.bot:
            return

        # fmt: off
        if len(reaction.message.embeds) != 1 \
        or reaction.message.embeds[0].title != self.text.get("stats", "title"):
            return
        # fmt: on

        embed = reaction.message.embeds[0]

        # get current offset
        if "," in embed.fields[0].name:
            offset = int(embed.fields[0].name.split(" ")[-1]) - 1
        else:
            offset = 0

        limit = self.config.get("limit")

        # get new offset
        if str(reaction) == "⏪":
            offset = 0
        elif str(reaction) == "◀":
            offset -= limit
        elif str(reaction) == "▶":
            offset += limit

        if offset < 0 or offset > len(self.usage):
            offset = 0

        # apply
        embed.clear_fields()

        if offset == 0:
            name = self.text.get("stats", "top_0", num=limit)
        else:
            name = self.text.get("stats", "top_n", num=limit, offset=offset + 1)

        embed.add_field(
            name=name,
            value=self.getCommandsStats(offset),
            inline=False,
        )

        await reaction.message.edit(embed=embed)
        await utils.remove_reaction(reaction, user)

    ##
    ## Helper functions
    ##

    async def _readFile(self, ctx: commands.Context, path: str):
        """Read file"""
        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            await self.output.error(ctx, "Log file not found")
            return None

        data = ""
        for line in lines:
            data += line
        return data

    def getCommandsStats(self, offset: int = 0) -> str:
        items = {
            k: v for k, v in sorted(self.usage.items(), key=lambda item: item[1], reverse=True)
        }

        template = "`{count:>3}` … {command}"
        content = []
        for i, (command, count) in enumerate(items.items()):
            if i < offset:
                continue
            if i >= self.config.get("limit") + offset:
                break
            content.append(template.format(count=count, command=command))

        if not len(content):
            return self.text.get("stats", "nothing")
        return "\n".join(content)
