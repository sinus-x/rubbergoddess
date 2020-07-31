import subprocess

from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import check, rubbercog, utils
from core.config import config


class Admin(rubbercog.Rubbercog):
    """Rubbergoddess administration"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("admin")
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

    @commands.cooldown(rate=2, per=20, type=commands.BucketType.channel)
    @commands.check(check.is_verified)
    @commands.command(name="commands")
    async def command_stats(self, ctx):
        """Command invocation statistics"""
        embed = self.embed(
            ctx=ctx,
            title=self.text.get("stats", "title"),
            description=self.text.get("stats", "description"),
        )

        num = self.config.get("stats_length")
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

        stats_length = self.config.get("stats_length")

        # get new offset
        if str(reaction) == "⏪":
            offset = 0
        elif str(reaction) == "◀":
            offset -= stats_length
        elif str(reaction) == "▶":
            offset += stats_length

        if offset > stats_length - len(self.usage):
            offset = len(self.usage) - stats_length - 1
        if offset < 0:
            offset = 0

        # apply
        embed.clear_fields()

        num = stats_length
        if len(self.usage) < num:
            num = len(self.usage)
        if offset == 0:
            name = self.text.get("stats", "top_0", num=num)
        else:
            name = self.text.get("stats", "top_n", num=num, offset=offset)
        top = "top_0" if offset == 0 else "top_n"

        embed.add_field(
            name=name, value=self.getCommandsStats(offset), inline=False,
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
            if i + offset > self.config.get("stats_length"):
                break

            content.append(template.format(count=count, command=command))

        if not len(content):
            return self.text.get("stats", "nothing")
        return "\n".join(content)


def setup(bot):
    bot.add_cog(Admin(bot))
