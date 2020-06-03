import discord
from discord.ext import commands

from core import rubbercog, check
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
        items.append(["nickname", self.price_nick])

        result = f"{'item':<12} price\n" + "-" * 18 + "\n"
        result += "\n".join([f"{x[0]:<12} {x[1]} k" for x in items])
        if len(items) == 0:
            result += "(No items)"
        await ctx.send("```" + result + "```")
        await self.deleteCommand(ctx)

    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.check(check.is_verified)
    @commands.group(name="nickname")
    async def nickname(self, ctx):
        """Change your nickname"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.invoked_with)

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @nickname.command(name="set")
    async def nickname_set(self, ctx, *, nick: str):
        """Set the nickname

        Use command `shop` to see prices

        nick: Your new nickname
        """
        # stop if user does not have nickname set
        if ctx.author.nick is None and nick is None:
            return await ctx.send_help(ctx.invoked_with)

        # check if user has karma
        user = repo_k.getMember(ctx.author.id)
        if user is None:
            return await ctx.send(text.get("shop", "no karma", author=ctx.author.mention))
        if user.karma < self.price_nick:
            return await ctx.send(
                text.fill(
                    "shop",
                    "not enough karma",
                    author=ctx.author.mention,
                    value=self.price_nick - user.karma,
                )
            )

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

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @nickname.command(name="unset")
    async def nickname_unset(self, ctx):
        """Unset the nickname"""
        if ctx.author.nick is None:
            return await ctx.send(text.get("shop", "no nick", author=ctx.author.mention))

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


def setup(bot):
    bot.add_cog(Shop(bot))
