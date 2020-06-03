import discord
from discord.ext import commands

from core import rubbercog, check
from core.text import text
from repository import user_repo, karma_repo

repo_u = user_repo.UserRepository()
repo_k = karma_repo.KarmaRepository()


class Interactions(rubbercog.Rubbercog):
    """Make use of your karma"""

    def __init__(self, bot):
        super().__init__(bot)

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

        nick: Your new nickname
        """
        # stop if user does not have nickname set
        if ctx.author.nick is None and nick is None:
            return await ctx.send_help(ctx.invoked_with)

        # check if user has karma
        user = repo_k.getMember(ctx.author.id)
        if user is None:
            return await ctx.send(text.get("interactions", "no karma", author=ctx.author.mention))
        if user.karma < 500:
            return await ctx.send(
                text.fill(
                    "interactions",
                    "not enough karma",
                    author=ctx.author.mention,
                    value=500 - user.karma,
                )
            )

        # set nickname
        try:
            await ctx.author.edit(nick=nick, reason="?nickname")
        except discord.Forbidden:
            return await ctx.send(text.get("error", "higher permission"))

        repo_k.updateMemberKarma(ctx.author.id, -500)
        await ctx.send(
            text.fill(
                "interactions",
                "new nick",
                author=ctx.author.mention,
                nick=discord.utils.escape_markdown(nick),
                value=500,
            )
        )

    @commands.cooldown(rate=1, per=3600 * 24, type=commands.BucketType.member)
    @nickname.command(name="unset")
    async def nickname_unset(self, ctx):
        """Unset the nickname"""
        if ctx.author.nick is None:
            return await ctx.send(text.get("interactions", "no nick", author=ctx.author.mention))

        nick = ctx.author.nick

        await ctx.author.edit(nick=None, reason="?nickname unset")
        await ctx.send(
            text.fill(
                "interactions",
                "nick removed",
                author=ctx.author.mention,
                nick=discord.utils.escape_markdown(nick),
            )
        )


def setup(bot):
    bot.add_cog(Interactions(bot))
