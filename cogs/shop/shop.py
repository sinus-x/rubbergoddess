import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from repository import user_repo, karma_repo

repo_u = user_repo.UserRepository()
repo_k = karma_repo.KarmaRepository()


class Shop(rubbercog.Rubbercog):
    """Make use of your karma"""

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("shop")
        self.text = CogText("shop")

    @commands.command()
    async def shop(self, ctx):
        """Display prices for various services"""
        embed = self.embed(ctx=ctx)

        items = ("nickname",)

        prices = []
        template = "`{item:<12}` … {price} k"
        for item in items:
            price_tag = template.format(item=item, price=self.config.get("prices", item))
            prices.append(price_tag)
        embed.add_field(name="\u200b", value="\n".join(prices))

        await ctx.send(embed=embed)
        await utils.delete(ctx)
        await utils.room_check(ctx)

    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.check(acl.check)
    @commands.group(name="nickname")
    async def nickname(self, ctx):
        """Change your nickname"""
        await utils.send_help(ctx)

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @commands.check(acl.check)
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
            return await ctx.send(self.text.get("no_karma", mention=ctx.author.mention))
        if user.karma < self.price_nick:
            return await ctx.send(
                self.text.get(
                    "not_enough_karma",
                    mention=ctx.author.mention,
                    value=self.price_nick - user.karma,
                )
            )

        if "@" in nick:
            raise ForbiddenNicknameCharacter("@")

        # set nickname
        try:
            await ctx.author.edit(nick=nick, reason="?nickname")
        except discord.Forbidden:
            return await ctx.send(self.text.get("higher_role"))

        repo_k.updateMemberKarma(ctx.author.id, -1 * self.price_nick)
        await ctx.send(
            self.text.get(
                "new_nick",
                mention=ctx.author.mention,
                nick=discord.utils.escape_markdown(nick),
                value=self.price_nick,
            )
        )
        await self.event.user(ctx, f"Nickname changed to {nick}.")

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @commands.check(acl.check)
    @nickname.command(name="unset")
    async def nickname_unset(self, ctx):
        """Unset the nickname"""
        if ctx.author.nick is None:
            return await ctx.send(self.text.get("no_nick", mention=ctx.author.mention))

        nick = ctx.author.nick

        await ctx.author.edit(nick=None, reason="?nickname unset")
        await ctx.send(
            self.text.get(
                "nick_removed",
                mention=ctx.author.mention,
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
            await self.output.error(ctx, self.text.get(
                "ForbiddenNicknameCharacter", characters=error.forbidden))

        # exceptions without parameters
        elif isinstance(error, ShopException):
            await self.output.error(ctx, self.text.get(type(error).__name__))
        # fmt: on


##
## Exceptions
##


class ShopException(rubbercog.RubbercogException):
    pass


class ForbiddenNicknameCharacter(ShopException):
    def __init__(self, forbidden: str):
        super().__init__()
        self.forbidden = forbidden
