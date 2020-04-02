import utils
import traceback
import discord
from discord.ext import commands

from config.config import Config as config
from config.messages import Messages as messages
from config.emotes import Emotes as emote

class Errors(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error (self, ctx: commands.Context, error):
        """Handle errors"""

        if isinstance(error, commands.MissingPermissions):
            await self._getNotification(ctx, messages.exc_no_permission)
            return

        if isinstance(error, commands.CommandOnCooldown):
            await self._getNotification(ctx, messages.exc_cooldown)
            return

        elif isinstance(error, commands.CheckFailure):
            await self._getNotification(ctx, messages.exc_no_requirements)
            return

        elif isinstance(error, commands.CommandNotFound):
            if not ctx.message.content[0] in config.command_prefix:
                await self._getNotification(ctx, messages.exc_no_command)
            return

        elif isinstance(error, commands.ExtensionError):
            await self._getError(ctx, messages.exc_extension_err)
            return

        # display error message
        await self._getError(ctx, ctx.message.content)

        output = 'Ignoring exception in command {}: \n\n'.format(ctx.command)
        output += ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        # print traceback to stdout
        print(output)
        # send traceback to dedicated channel
        channel = self.bot.get_channel(config.bot_dev_channel)
        output = list(output[0+i:1960+i] for i in range(0, len(output), 1960))
        if channel is not None:
            for message in output:
                await channel.send("```\n{}```".format(message))


    ##
    ## HELPER FUNCTIONS
    ##

    def _getEmbedTitle (self, ctx: commands.Context):
        """Create title for command embed"""
        c = ctx.command
        p = ' '.join((p.name) for p in c.parents) + " " if c.parents else ""
        t = config.default_prefix + p + c.name
        return t

    def _getEmbed (self, ctx: commands.Context, color: str = None, pin = False):
        """Create embed for command info/notification/error

        color: embed color
        pin: wheter to pin the embed or let it be deleted
        """
        if color not in [config.color_success, config.color_error, config.color_notify]:
            color = config.color
        t = self._getEmbedTitle()
        if pin is not None and pin:
            t = "📌 " + t
        d = "**{}** cog".format(c.cog_name)
        embed = discord.Embed(color=color,
            title=t, description=d, delete_after=config.delay_embed)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        return embed


    async def _getError (self, ctx: commands.Context, errmsg: str,
                               delete: bool = True, pin: bool = None):
        """Show embed with an error"""
        embed = self._getEmbed(ctx, color=config.color_error, pin=pin)
        embed.add_field(name="Error occured", value=errmsg, inline=False)
        embed.add_field(name="Command", value=ctx.message.content, inline=False)
        if delete:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        else:
            await ctx.send(embed=embed)
        await self._tryDelete(ctx, now=True)

    async def _getNotification (self, ctx: commands.Context, msg: str,
                                    pin: bool = False):
        """Show embed with a notification"""
        embed = self._getEmbed(ctx, color=config.color_notify, pin=pin)
        embed.add_field(name="Notification", value=msg, inline=False)
        embed.add_field(name="Command", value=ctx.message.content, inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx, now=True)


    async def _getDescription (self, ctx: commands.Context):
        """Show description for command"""
        embed = self._getEmbed(ctx)
        embed.add_field(name="Description", value=ctx.command.short_doc)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx, now=True)

    async def _getHelp (self, ctx: commands.Context):
        """Show parameters for command"""
        #TODO add bold text to the first line and parameter names
        embed = self._getEmbed(ctx)
        embed.add_field(name="Help", value=ctx.command.help)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx, now=False)

    #TODO Sort options
    async def _getOptions (self, ctx: commands.Context):
        """Show commands available inside of a command group"""
        embed = self._getEmbed(ctx)
        if ctx.command.commands:
            for opt in ctx.command.commands:
                # ctx.command.commands are probably sorted as they are loaded,
                # eg. backwards. This is not 100% reliable, but it works,
                # generally
                embed.insert_field_at(index=0,
                    name=opt.name, value=opt.short_doc, inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self._tryDelete(ctx, now=True)



    async def _tryDelete (self, ctx: commands.Context, now: bool = False):
        """Try to delete the context message.

        now: On "now" string, do not wait for embed delay
        """
        try:
            if now:
                await ctx.message.delete()
            else:
                await ctx.message.delete(delay=config.delay_embed)
        except discord.HTTPException:
            pass



    #FIXME Can this be done in a dynamic way?
    #FIXME Can these functions be here?
    def _parsePin (self, pin):
        """Return True only if pin is 'pin'"""
        return pin is not None and pin == "pin"
    def _parseForce (self, force):
        """Return True only if force is 'force'"""
        return force is not None and force == "force"


def setup(bot):
    bot.add_cog(Errors(bot))
