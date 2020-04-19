import subprocess

import discord
from discord.ext import commands

from core import rubbercog
from config.config import config
from config.messages import Messages as messages

class Admin(rubbercog.Rubbercog):
    """Rubbergoddess administration"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

    @commands.group(name="config")
    @commands.has_permissions(administrator=True)
    async def config(self, ctx: commands.Context):
        """Edit bot configuration"""
        if ctx.invoked_subcommand is None:
            self.throwHelp(ctx)
            return

    @config.command(name="set")
    async def config_set(self, ctx: commands.Command, key: str, value: str):
        """Set config key"""
        self.throwNotification(messages.err_not_implemented)
        return

    @config.command(name="discard")
    async def config_discard(self, ctx: commands.Command, key: str):
        """Discard config change"""
        self.throwNotification(messages.err_not_implemented)
        return

    @config.command(name="save")
    async def config_save(self, ctx: commands.Context):
        """Save edited config file"""
        self.throwNotification(messages.err_not_implemented)
        return

    @commands.command(name="restart")
    @commands.has_permissions(administrator=True)
    async def restart(self, ctx: commands.Context):
        """Restart Rubbergoddess"""
        self.throwNotification(messages.err_not_implemented)
        return

        """
        standalone systemd docker systemd+docker
        YES        YES     DOCKER DOCKER
        """

    @commands.command(name="log")
    @commands.has_permissions(administrator=True)
    async def log(self, ctx: commands.Context, target: str = None):
        """See bot logs

        target: service (systemd), bot (python), cron (database backups); none ~ service+bot
        """
        # loader = [ standalone, docker, systemd, systemd+docker ]
        # target = [ service+bot, service, bot, cron ]
        if target not in ["service", "bot", "cron"]:
            target = "service+bot"
        cmd = ""

        if config.loader is "docker":
            await self.throwNotification(ctx, messages.err_not_supported)
            return
        
        elif config.loader is "systemd+docker":
            if target is "bot":
                await self.throwNotification(ctx, messages.err_not_implemented)
                return
            else:
                await self.throwNotification(ctx, messages.err_not_supported)
                return

        elif config.loader is "standalone":
            if "service" in target:
                await self.throwNotification(ctx, messages.err_not_supported)
                return
            else:
                await self.throwNotification(ctx, messages.err_not_implemented)
                return

        elif config.loader is "systemd":
            cmd = "sudo journalctl -u rubbergoddess"

        try:
            stdout = subprocess.check_output(cmd, shell=True).decode("utf-8")
        except subprocess.CalledProcessError as e:
            await ctx.send(e)
            print(e)
            return
        output = list(stdout[0+i:1960+i] for i in range(0, len(stdout), 1960))
        for o in output:
            await ctx.send("```{}```".format(o))
        await self.deleteCommand(ctx)


        """         standalone systemd docker systemd+docker
        service+bot NO         YES     NO     NO
        service     NO         YES     NO     NO
        bot         YES        YES     NO     MAYBE
        cron        YES        YES     NO     NO             """


def setup(bot):
    bot.add_cog(Admin(bot))
