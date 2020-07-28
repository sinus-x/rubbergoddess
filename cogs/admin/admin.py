import subprocess

from discord.ext import commands

from cogs.resource import CogText
from core import check, rubbercog, utils
from core.config import config


class Admin(rubbercog.Rubbercog):
    """Rubbergoddess administration"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("admin")

        self.usage = {}

    ##
    ## Commands
    ##

    @commands.is_owner()
    @commands.group(name="system")
    async def system(self, ctx):
        """Prepare the guild for shutdown"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

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

    @system.command(name="shutdown")
    async def system_shutdown(self, ctx):
        """Shutdown the bot"""
        await self.event.sudo(ctx, "System shutdown.")
        await self.console.critical(ctx, "System shutdown initiated.")
        await self.bot.logout()

    @commands.command(name="status")
    @commands.check(check.is_mod)
    @commands.check(check.is_in_modroom)
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

    @commands.command(name="journalctl")
    @commands.check(check.is_mod)
    @commands.check(check.is_in_modroom)
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

    @commands.check(check.is_mod)
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

    @commands.is_owner()
    @commands.command(name="commands")
    async def command_stats(self, ctx):
        """Command invocation statistics"""
        items = {
            k: v for k, v in sorted(self.usage.items(), key=lambda item: item[1], reverse=True)
        }

        content = []
        content.append(">>> **{}**".format(self.text.get("stats", "title").upper()))
        total = 0
        template = "`{count:>3}` … {command}"
        for command, count in items.items():
            content.append(template.format(count=count, command=command))
            total += count
        if len(content) == 0:
            content.append(self.text.get("stats", "nothing"))

        result = ""
        for line in content:
            if len(result) + len(line) > 2000:
                await ctx.send(result)
                result = ""
            result += "\n" + line
        await ctx.send(result)

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


def setup(bot):
    bot.add_cog(Admin(bot))
