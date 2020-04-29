import re

import discord
from discord.ext import commands

from core.config import config
from core.text import text
from core import check, rubbercog, utils

class Janitor(rubbercog.Rubbercog):
    """Manage channels"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

    async def is_in_modroom(ctx):
        return ctx.message.channel.id == config.channel_mods

    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(is_in_modroom)	
    @commands.has_permissions(administrator=True)	
    @commands.command()	
    async def hoarders(self, ctx: commands.Context):
        message = tuple(re.split(r'\s+', str(ctx.message.content).strip("\r\n\t")))
        guild = self.bot.get_guild(config.guild_id)
        members = guild.members
        channel = ctx.channel
        if len(message) == 2 and message[1] == "warn":
            warn = True
        else:
            warn = False

        hoarders = []
        for member in members:	
            prog =[]
            for role in member.roles:	
                if role < discord.utils.get(guild.roles, name='---FEKT') and role > discord.utils.get(guild.roles, name='---'):	
                    prog.append(role.name)
            if len(prog) > 1:	
                hoarders.append([member, prog])

        if len(hoarders) == 0:	
            await ctx.send(text.get("warden","no hoarders"))	
        else:
            all = len(hoarders)
            currnum = 1
            if warn:
                mess = await ctx.send("Odesílání zprávy {curnum}/{all}.".format(curnum=currnum, all=all))
            embed = discord.Embed(title="Programme hoarders", color=config.color)	
            for member, programmes in hoarders:
                embed.add_field(name="User", value=member.mention, inline = True)
                embed.add_field(name="Status", value=member.status, inline = True)
                embed.add_field(name="Programmes", value=', '.join(programmes), inline = True)
                if warn:
                    if currnum %5:
                        await mess.edit(content="Odesílání zprávy {curnum}/{all}.".format(curnum=currnum, all=all))
                    await member.send(utils.fill_message("hoarders_warn", user=member.id))
                currnum += 1
            if warn:
                currnum -= 1
                await mess.edit(content="Odesílání zprávy {curnum}/{all}.".format(curnum=currnum, all=all))
            await channel.send(embed=embed)

    @commands.check(check.is_mod)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command()
    async def purge(self, ctx: commands.Context, channel: discord.TextChannel = None, *params):
        """Delete messages from channel

        channel: A text channel
        limit: Optional. How many messages to delete. If not present, delete all
        users: Optional. Only selected user IDs.
        pins: Optional. How to treat pinned posts. 'skip' (default), 'stop', 'ignore'
        """
        await self.throwNotification(ctx, text.get("error", "not implemented"))
        return

        if channel is None:
            await self.throwHelp(ctx)
            return

        # get parameters
        #FIXME Can this be done in a cleaner way? 
        limit = None
        pins = "skip"
        users = None
        for param in params:
            if param.startswith("limit="):
                try:
                    limit = int(param.replace("limit=",""))
                except ValueError:
                    self.throwHelp(ctx)
                    return
            elif param.startswith("pins="):
                if value.replace("pins=", "") in ["stop", "ignore"]:
                    pins = value.replace("pins=","")
                else:
                    self.throwHelp(ctx)
                    return
            elif param.startswith("users="):
                try:
                    users = [int(x) for x in param.replace("users=","").split(",")]
                except ValueError:
                    self.throwHelp(ctx)
                    return

        #TODO Try to do purge()
        #     Then check how many messages were deleted. On pinSkip() and pinStop()
        #     we have to go one-by-one.
        #TODO generate report

def setup(bot):
    bot.add_cog(Janitor(bot))
