import discord
from discord.ext import commands

from core import rubbercog, check, utils
from core.config import config
from core.text import text
from repository import user_repo, karma_repo

repo_u = user_repo.UserRepository()
repo_k = karma_repo.KarmaRepository()


class Shop(rubbercog.Rubbercog):
    """Make use of your karma"""

    def __init__(self, bot):
        super().__init__(bot)
        self.price_nick = config.get("shop", "nickname")

    @commands.command()
    async def shop(self, ctx):
        """Display prices for various services"""
        items = []
        template = "`{item:<12} … {price} k"
        items.append(template.format(item="nickname", price=self.price_nick))
        content = "\n".join(items)

        embed = self.embed(ctx=ctx)
        embed.add_field(name="\u200b", value=content)
        await ctx.send(embed=embed, delete_after=config.get("delay", "help"))

        await utils.delete(ctx)

    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.check(check.is_verified)
    @commands.group(name="nickname")
    async def nickname(self, ctx):
        """Change your nickname"""
        await utils.send_help(ctx)

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @nickname.command(name="set")
    async def nickname_set(self, ctx, *, nick: str):
        """Set the nickname

        Use command `shop` to see prices

        nick: Your new nickname
        """
        # stop if user does not have nickname set
        if ctx.author.nick is None and nick is None:
            return await utils.send_help(ctx)

        # check if user has karma
        user = repo_k.getMember(ctx.author.id)
        if user is None:
            return await ctx.send(text.fill("shop", "no karma", author=ctx.author.mention))
        if user.karma < self.price_nick:
            return await ctx.send(
                text.fill(
                    "shop",
                    "not enough karma",
                    author=ctx.author.mention,
                    value=self.price_nick - user.karma,
                )
            )

        if "@" in nick:
            raise ForbiddenNicknameCharacter("@")

        # set nickname
        try:
            await ctx.author.edit(nick=nick, reason="?nickname")
        except discord.Forbidden:
            return await ctx.send(text.get("error", "higher permission"))

        repo_k.updateMemberKarma(ctx.author.id, -1 * self.price_nick)
        await ctx.send(
            text.fill(
                "shop",
                "new nick",
                author=ctx.author.mention,
                nick=discord.utils.escape_markdown(nick),
                value=self.price_nick,
            )
        )
        await self.event.user(ctx, f"Nickname changed to {nick}.")

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @nickname.command(name="unset")
    async def nickname_unset(self, ctx):
        """Unset the nickname"""
        if ctx.author.nick is None:
            return await ctx.send(text.fill("shop", "no nick", author=ctx.author.mention))

        nick = ctx.author.nick

        await ctx.author.edit(nick=None, reason="?nickname unset")
        await ctx.send(
            text.fill(
                "shop",
                "nick removed",
                author=ctx.author.mention,
                nick=discord.utils.escape_markdown(nick),
            )
        )
        await self.event.user(ctx, "Nickname reset.")

    ##
    ## Error catching
    ##

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # try to get original error
        if hasattr(ctx.command, "on_error") or hasattr(ctx.command, "on_command_error"):
            return
        error = getattr(error, "original", error)

        # non-rubbergoddess exceptions are handled globally
        if not isinstance(error, rubbercog.RubbercogException):
            return

        # fmt: off
        # exceptions with parameters
        if isinstance(error, ForbiddenNicknameCharacter):
            await self.output.error(ctx, text.fill(
                "shop", "ForbiddenNicknameCharacter", characters=error.forbidden))

        # exceptions without parameters
        elif isinstance(error, ShopException):
            await self.output.error(ctx, text.get("shop", type(error).__name__))
        # fmt: on


def setup(bot):
    bot.add_cog(Shop(bot))


##
## Exceptions
##


class ShopException(rubbercog.RubbercogException):
    pass


class ForbiddenNicknameCharacter(ShopException):
    def __init__(self, forbidden: str):
        super().__init__()
        self.forbidden = forbidden
