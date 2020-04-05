import discord
from discord.ext import commands

from core import utils
from config.config import config
from config.messages import Messages as messages

class Rubbercog (commands.Cog):
    """Main cog class"""
    visible = True

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    ##
    ## Helper functions
    ##
    def _getEmbedTitle (self, ctx: commands.Context):
        """Helper function assembling title for embeds"""
        if ctx.command is None:
            return "(no command)"

        path = ' '.join((p.name) for p in ctx.command.parents) + \
               ' ' if ctx.command.parents else ''
        return config.prefix + path + ctx.command.name

    def _getEmbed (self, ctx: commands.Context, color: int = None, pin = False):
        """Helper function for creating embeds

        color: embed color
        pin: whether to pin the embed or let it be deleted
        """
        if color not in config.colors:
            color = config.color
        if pin is not None and pin:
            title = "📌 " + self._getEmbedTitle(ctx)
        else:
            title = self._getEmbedTitle(ctx)
        description = "**{}**".format(ctx.command.cog_name) if ctx.command else ''

        embed = discord.Embed(title=title, description=description, color=color)
        if ctx.author is not None:
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        return embed

    async def deleteCommand(self, ctx: commands.Context, now: bool = True):
        """Try to delete the context message.

        now: Do not wait for message delay"""
        delay = 0.0 if now else config.delay_embed
        try:
            await ctx.message.delete(delay=delay)
        except discord.HTTPException as err:
            self.logException(ctx, err)
            pass

    ##
    ## Utils
    ##
    def logError (self, ctx: commands.Context):
        """Save event into the server log channel"""
        channel = self.bot.get_channel(config.guildlog)
        channel.send(utils.fill_message(
            "log_error", channel=ctx.channel, user=ctx.author.id,
            command=ctx.message.content))

    def logException (self, ctx:commands.Context, error):
        """Save exception to the server log channel"""
        channel = self.bot.get_channel(config.guildlog)
        channel.send(utils.fill_message(
            "log_exception", channel=ctx.channel, user=ctx.author.id,
            command=ctx.message.content, error=error))

    def parseArg (self, arg: str = None):
        """Return true if supported argument is matched"""
        #TODO Do this the proper way
        args = ["pin", "force"]
        return True if arg in args else False


    ##
    ## Embeds
    ##
    async def throwError (self, ctx: commands.Context, errmsg: str,
                                delete: bool = False, pin: bool = None):
        """Show an embed with thrown error."""
        embed = self._getEmbed(ctx, color=config.color_error, pin=pin)
        embed.add_field(name="Nastala chyba", value=errmsg, inline=False)
        embed.add_field(name="Příkaz", value=ctx.message.content, inline=False)
        delete = False if pin else delete
        if delete:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        else:
            await ctx.send(embed=embed)
        await self.deleteCommand(ctx, now=True)

    async def throwNotify (self, ctx: commands.Context, msg: str,
                                 pin: bool = False):
        """Show an embed with a message."""
        embed = self._getEmbed(ctx, color=config.color_notify, pin=pin)
        embed.add_field(name="Upozornění", value=msg, inline=False)
        embed.add_field(name="Příkaz", value=ctx.message.content, inline=False)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)

    async def throwDescription (self, ctx: commands.Context, pin: bool = False):
        """Show an embed with full docstring content."""
        #TODO Make first line and parameters bold
        embed = self._getEmbed(ctx)
        embed.add_field(name="O funkci", value=ctx.command.short_doc)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)
        
    async def throwHelp (self, ctx: commands.Context, pin: bool = False):
        """Show an embed with help. Show options for groups"""
        embed = self._getEmbed(ctx)
        embed.add_field(name="Nápověda", value=ctx.command.help)

        if isinstance(ctx.command, commands.Group) and ctx.command.commands:
            for opt in sorted(ctx.command.commands):
                embed.add_field(name=opt.name, value=opt.short_doc, inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)
