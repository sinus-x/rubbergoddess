import subprocess
import asyncio

from discord.ext import commands

from core import check, rubbercog
from core.config import config
from core.emote import emote
from core.text import text
from config.messages import Messages as messages


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

    @commands.command(name="restart", aliases=["reboot"])
    @commands.check(check.is_bot_owner)
    @commands.check(check.is_in_modroom)
    async def restart(self, ctx: commands.Context, target: str = None):
        """Restart Rubbergoddess

        target: Optional. [ all (default) | docker ]
        """
        await self.throwNotification(messages.err_not_implemented)
        return

        if target != "docker":
            target = None

        cmd = ""
        stdout = None
        """
        Current state:
        standalone systemd docker systemd+docker
        YES        YES     DOCKER DOCKER
        """

        if config.loader == "standalone":
            await self.throwNotification(ctx, messages.err_not_supported + " (nohup)")
            return

        elif config.loader in ["docker", "systemd+docker"]:
            if target == "docker":
                # FIXME Can this help with anything? It doesn't even reload
                #      the changes in the code.
                await ctx.send("Za chvíli budu zpátky. Restartuji Docker kontejner :wave:")
                cmd = "docker restart rubbergoddess_bot_1"
            else:
                await self.throwNotification(
                    ctx, "Jsem zavřená v Dockeru a ještě se neumím dostat ven " + emote.sad
                )
                return

        elif config.loader == "systemd":
            await ctx.send("Za chvíli budou zpátky. Restartuji systemd službu :wave:")
            cmd = "sudo systemctl restart rubbergoddess"

        else:
            await self.throwError(ctx, "Invalid config.loader option")
            return

        await self.log(ctx, "Restart", msg=config.loader)
        try:
            print("Restarting (" + config.loader + "): " + self.getTimestamp())
            stdout = subprocess.check_output(cmd, shell=True).decode("utf-8")
        except subprocess.CalledProcessError as e:
            print(e)
            await self.throwError(ctx, e)
            return

        asyncio.sleep(4)
        if len(stdout) > 1900:
            stdout = stdout[:1900]
        await self.throwError(ctx, "Restarting error", "\n" + stdout)

    @commands.command(name="status")
    @commands.check(check.is_mod)
    @commands.check(check.is_in_modroom)
    async def status(self, ctx: commands.Context):
        """Display systemd status"""
        if config.loader != "systemd":
            await ctx.send("Neběžím přímo v systemd, tak to neumím " + emote.sad)
            await self.deleteCommand(ctx)
            return

        stdout = None
        try:
            stdout = subprocess.check_output(
                "sudo systemctl status rubbergoddess", shell=True
            ).decode("utf-8")
        except subprocess.CalledProcessError as e:
            await self.throwError(ctx, e)
            return

        await ctx.send("```\n{}\n```".format(stdout))

    @commands.command(name="journalctl")
    @commands.check(check.is_mod)
    @commands.check(check.is_in_modroom)
    async def journalctl(self, ctx: commands.Context, target: str = None):
        """See bot logs

        target: Optional. [ bot (default) | cron ]
        """
        target = "cron" if target == "cron" else "bot"
        cmd = None
        file = None
        stdout = None
        """
                standalone systemd docker systemd+docker
        bot     YES        YES     YES    MIRROR
        cron    YES        YES     MIRROR MIRROR         """

        if config.loader == "standalone":
            if target == "bot":
                file = await self._readFile(ctx, "rubbergoddess.log", docker=False)
            elif target == "cron":
                file = await self._readFile(ctx, "journalctl.log", docker=False)

        elif config.loader == "systemd":
            if target == "bot":
                cmd = "sudo journalctl -u rubbergoddess"
            elif target == "cron":
                file = await self._readFile(ctx, "journalctl.log", docker=False)

        elif config.loader == "docker":
            if target == "bot":
                cmd = "docker logs rubbergoddess_bot_1"
            elif target == "cron":
                file = await self._readFile(ctx, "rubbergoddess.log", docker=True)

        elif config.loader == "systemd+docker":
            if target == "bot":
                file = await self._readFile(ctx, "journalctl.log", docker=True)
            elif target == "cron":
                file = await self._readFile(ctx, "rubbergoddess.log", docker=True)

        else:
            await self.throwError(ctx, "Unsupported value for 'loader' config key")
            return

        if cmd:
            try:
                stdout = subprocess.check_output(cmd + " | tail -n 40", shell=True).decode("utf-8")
            except subprocess.CalledProcessError as e:
                await self.throwError(ctx, e)
                return
        elif file is not None:
            stdout = file
        elif file is None:
            return

        output = list(stdout[0 + i : 1960 + i] for i in range(0, len(stdout), 1960))
        for o in output:
            await ctx.send("```{}```".format(o))
        await self.deleteCommand(ctx)

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
            await self.throwNotification(ctx, "Log file not found")
            await self.log(ctx, "Log not found", msg=path)
            return None

        data = ""
        for line in lines:
            data += line
        return data


def setup(bot):
    bot.add_cog(Admin(bot))
