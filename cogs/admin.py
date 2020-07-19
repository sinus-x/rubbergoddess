import subprocess

from discord.ext import commands

from core import check, rubbercog, utils
from core.config import config
from core.text import text


class Admin(rubbercog.Rubbercog):
    """Rubbergoddess administration"""

    def __init__(self, bot):
        super().__init__(bot)

    @commands.group(name="power")
    @commands.is_owner()
    async def power(self, ctx):
        """Prepare the guild for shutdown"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

    @power.command(name="off")
    async def power_off(self, ctx, *, reason: str = None):
        """Prepare for power off

        reason: Optional. The reason for shutdown
        """
        if reason is None:
            reason = ""
        else:
            reason = " " + text.fill("admin", "poweroff reason", reason=reason)

        jail = self.getGuild().get_channel(config.get("channels", "jail"))
        everyone = self.getGuild().default_role
        botspam = self.getGuild().get_channel(config.get("channels", "botspam"))

        visited = []

        if jail is not None:
            # send message
            await jail.send(text.get("admin", "poweroff jail") + reason)
            # switch to read-only
            await jail.set_permissions(everyone, send_messages=False, reason="?power off")
            visited.append(jail.mention)

        if botspam is not None:
            # send message
            await botspam.send(text.get("admin", "poweroff botspam") + reason)
            visited.append(botspam.mention)

        # send confirmation message
        if len(visited) > 0:
            await ctx.send(text.fill("admin", "poweroff ok", channels=", ".join(visited)))
        else:
            await ctx.send(text.fill("admin", "power fail"))
        await self.event.sudo(ctx, f"Power off: {reason}")

    @power.command(name="on")
    async def power_on(self, ctx):
        """Restore"""
        jail = self.getGuild().get_channel(config.get("channels", "jail"))
        everyone = self.getGuild().default_role
        botspam = self.getGuild().get_channel(config.get("channels", "botspam"))

        visited = []

        if jail is not None:
            # remove the message
            messages = await jail.history(limit=10).flatten()
            for message in messages:
                if message.content.startswith(text.get("admin", "poweroff jail")):
                    await message.delete()
                    break
            # switch to read-write
            await jail.set_permissions(everyone, send_messages=True, reason="?power on")
            visited.append(jail.mention)

        if botspam is not None:
            # send message
            await botspam.send(text.get("admin", "poweron botspam"))
            visited.append(botspam.mention)

        # send confirmation message
        if len(visited) > 0:
            await ctx.send(text.fill("admin", "poweron ok", channels=", ".join(visited)))
        else:
            await ctx.send(text.fill("admin", "power fail"))
        await self.event.sudo(ctx, "Power on")

    @commands.command(name="status")
    @commands.check(check.is_mod)
    @commands.check(check.is_in_modroom)
    async def status(self, ctx: commands.Context):
        """Display systemd status"""
        if config.loader != "systemd":
            return await ctx.send(text.get("admin", "not systemd"))

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
            result = await self._readFile(ctx, "rubbergoddess.log", docker=False)
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
        embed.add_field(name="Host machine", value=config.get("bot", "host"))
        embed.add_field(name="Loader", value=config.get("bot", "loader"))
        # logging
        embed.add_field(name="Logging", value=config.get("bot", "logging"))
        # extensions
        embed.add_field(
            name="Default extensions",
            value=", ".join([x.lower() for x in sorted(config.get("bot", "extensions"))]),
            inline=False,
        )
        embed.add_field(
            name="Loaded extensions",
            value=", ".join([x.lower() for x in sorted(self.bot.cogs.keys()) if x != "Errors"]),
            inline=False,
        )
        # fmt: on

        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await utils.delete(ctx)

    async def _readFile(self, ctx: commands.Context, file: str, docker: bool):
        """Read file

        file: path to file
        docker: [ True | False ] Read from docker filesystem?
        """
        if docker:
            path = "/rubbergoddess/" + file
        else:
            path = file

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
