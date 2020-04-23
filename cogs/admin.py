import subprocess

import discord
from discord.ext import commands

from core import rubbercog, check
from config.config import config
from config.messages import Messages as messages
from config.emotes import Emotes as emote

class Admin(rubbercog.Rubbercog):
    """Rubbergoddess administration"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

    @commands.group(name="config")
    @commands.check(check.is_bot_owner)
    @commands.check(check.is_in_modroom)
    async def config(self, ctx: commands.Context):
        """Edit bot configuration"""
        if ctx.invoked_subcommand is None:
            await self.throwHelp(ctx)
            return

    @config.command(name="set")
    async def config_set(self, ctx: commands.Command, key: str, value: str):
        """Set config key"""
        await self.throwNotification(messages.err_not_implemented)
        return

    @config.command(name="discard")
    async def config_discard(self, ctx: commands.Command, key: str):
        """Discard config change"""
        await self.throwNotification(messages.err_not_implemented)
        return

    @config.command(name="save")
    async def config_save(self, ctx: commands.Context):
        """Save edited config file"""
        await self.throwNotification(messages.err_not_implemented)
        return

    @commands.command(name="restart", aliases=["reboot"])
    @commands.check(check.is_bot_owner)
    @commands.check(check.is_in_modroom)
    async def restart(self, ctx: commands.Context, target: str = None):
        """Restart Rubbergoddess

        target: Optional. [ all (default) | docker ]
        """
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
                #FIXME Can this help with anything? It doesn't even reload 
                #      the changes in the code.
                await ctx.send("Za chvíli budu zpátky. Restartuji Docker kontejner :wave:")
                cmd = "docker restart rubbergoddess_bot_1"
            else:
                await self.throwNotification(ctx, 
                    "Jsem zavřená v Dockeru a ještě se neumím dostat ven " + emote.sad)
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

        # If we run the following, an error occured, because the bot did not halt.
        # Probably. There may be some delay I assume.
        if len(stdout) > 1900:
            stdout = stdout[:1900]
        await self.throwError(ctx, "Restarting error", "\n"+stdout)

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
                "sudo systemctl status rubbergoddess", shell=True).decode("utf-8")
        except subprocess. CalledProcessError as e:
            await self.throwError(ctx, e)
            return

        await ctx.send("```\n{}\n```".format(stdout))


    @commands.command(name="log")
    @commands.check(check.is_mod)
    @commands.check(check.is_in_modroom)
    async def getLog(self, ctx: commands.Context, target: str = None):
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
                file = await self._readFile(ctx, "journalctl.log",    docker=False)

        elif config.loader == "systemd":
            if target == "bot":
                cmd = "sudo journalctl -u rubbergoddess"
            elif target == "cron":
                file = await self._readFile(ctx, "journalctl.log",    docker=False)

        elif config.loader == "docker":
            if target == "bot":
                cmd = "docker logs rubbergoddess_bot_1"
            elif target == "cron":
                file = await self._readFile(ctx, "rubbergoddess.log", docker=True)

        elif config.loader == "systemd+docker":
            if target == "bot":
                file = await self._readFile(ctx, "journalctl.log",    docker=True)
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

        output = list(stdout[0+i:1960+i] for i in range(0, len(stdout), 1960))
        for o in output:
            await ctx.send("```{}```".format(o))
        await self.deleteCommand(ctx)

    async def _readFile(self, ctx: commands.Context, file: str, docker: bool):
        """Read file
        
        file: path to file
        docker: [ True | False ] Read from docker filesystem?
        """
        if docker:
            path = '/rubbergoddess/' + file
        else:
            path = file

        try:
            with open(path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError as e:
            await self.throwNotification(ctx, "Log file not found")
            await self.log(ctx, "Log not found", msg=path)
            return None

        data = ""
        for line in lines:
            data += line
        return data

def setup(bot):
    bot.add_cog(Admin(bot))
