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

        self.guild = None
        self.role_mod = None
        self.role_verify = None
        self.roles_elevated = None


    ##
    ## OBJECT GETTERS
    ##
    def getGuild(self):
        if self.guild is None:
            self.guild = self.bot.get_guild(config.guild_id)
        return self.guild
    def getModRole(self):
        if self.role_mod is None:
            self.role_mod = self.getGuild().get_role(config.role_mod)
        return self.role_mod
    def getVerifyRole(self):
        if self.role_verify is None:
            self.role_verify = self.getGuild().get_role(config.role_verify)
        return self.role_verify
    def getElevatedRoles(self):
        return
        #TODO


    ##
    ## Helper functions
    ##
    def _getEmbedTitle(self, ctx: commands.Context):
        """Helper function assembling title for embeds"""
        #TODO Make sure parents are in right order - `?update database login` occurs
        if ctx.command is None:
            return "(no command)"

        path = ' '.join((p.name) for p in ctx.command.parents[::-1]) + \
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

    def _getCommandSignature(self, ctx: commands.Context):
        """Return a 'cog:command_name' string"""
        if not ctx.command:
            return 'UNKNOWN'
        return "{}:{}".format(ctx.command.cog.lower(),
            ctx.command.qualified_name.replace(" ", "_"))

    ##
    ## Utils
    ##
    async def log (self, ctx, action: str, quote: bool = True, error = None):
        """Log event"""
        channel = self.getGuild().get_channel(config.channel_guildlog)
        if ctx.author.top_role.id in config.roles_elevated:
            user = "{r} **{u}**".format(u=ctx.author.name, r=ctx.author.top_role.name.lower())
        else:
            user = ctx.author.mention
        msg = "**{}** by {} in {}".format(action, user, ctx.channel.mention)
        if error or quote:
            msg += ": "
        if error:
            msg += type(error).__name__
        if quote:
            msg += "\n> _{}_".format(ctx.message.content)
        await channel.send(msg)
        #TODO Save to log

    async def deleteCommand(self, ctx: commands.Context, now: bool = True):
        """Try to delete the context message.

        now: Do not wait for message delay"""
        delay = 0.0 if now else config.delay_embed
        try:
            await ctx.message.delete(delay=delay)
        except discord.HTTPException as err:
            self.logException(ctx, err)
            pass

    def parseArg (self, arg: str = None):
        """Return true if supported argument is matched"""
        #TODO Do this the proper way
        args = ["pin", "force"]
        return True if arg in args else False


    ##
    ## Embeds
    ##
    #TODO Make wrapper function for these two, they are quite similar
    async def throwError (self, ctx: commands.Context, err,
                                delete: bool = False, pin: bool = None):
        """Show an embed with thrown error."""
        content = ctx.message.content
        if len(str(content)) > 512:
            content = str(content)[:512]
        embed = self._getEmbed(ctx, color=config.color_error, pin=pin)
        e = type(err).__name__
        embed.add_field(name="Error occured", value=e, inline=False)
        embed.add_field(name="Command", value=content, inline=False)
        delete = False if pin else delete
        if delete:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        else:
            await ctx.send(embed=embed)
        await self.deleteCommand(ctx, now=True)
        await self.log(ctx, self._getCommandSignature(ctx), quote=True, error=err)


    async def throwNotification (self, ctx: commands.Context, msg: str,
                                 pin: bool = False):
        """Show an embed with a message."""
        content = ctx.message.content
        if len(str(content)) > 512:
            content = str(content)[:512]
        embed = self._getEmbed(ctx, color=config.color_notify, pin=pin)
        embed.add_field(name="Notification", value=msg, inline=False)
        embed.add_field(name="Command", value=content, inline=False)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)


    async def throwDescription (self, ctx: commands.Context, pin: bool = False):
        """Show an embed with full docstring content."""
        #TODO Make first line and parameters bold
        embed = self._getEmbed(ctx)
        embed.add_field(name="About", value=ctx.command.short_doc)
        if pin:
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)
        

    async def throwHelp (self, ctx: commands.Context, pin: bool = False):
        """Show an embed with help. Show options for groups"""
        embed = self._getEmbed(ctx)
        embed.add_field(name="Help", value=ctx.command.help)

        if isinstance(ctx.command, commands.Group) and ctx.command.commands:
            embed.add_field(name="-"*60, value="**SUBCOMMANDS**:", inline=False)
            #TODO Sort by lambda or something
            for opt in ctx.command.commands:
                embed.add_field(name=opt.name, value=opt.short_doc, inline=False)
        await ctx.send(embed=embed, delete_after=config.delay_embed)
        await self.deleteCommand(ctx, now=True)
