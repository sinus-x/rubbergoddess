import discord
from discord.ext import commands

from core import rubbercog, utils
from core.config import config
from features import karma, reaction
from repository import karma_repo

karma_r = karma_repo.KarmaRepository()


class Karma(rubbercog.Rubbercog):
    """User karma commands"""

    def __init__(self, bot):
        super().__init__(bot)
        self.karma = karma.Karma(bot, karma_r)
        self.reaction = reaction.Reaction(bot, karma_r)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            await self.reaction.add(payload)
        except discord.HTTPException:
            # ignore HTTP Exceptions
            return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        try:
            await self.reaction.remove(payload)
        except discord.HTTPException:
            # ignore HTTP Exceptions
            return

    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.user)
    @commands.command(name="karma")
    async def pick_karma_command(self, ctx, *args):
        karma = self.karma
        if len(args) == 0:
            await ctx.send(karma.karma_get(ctx.author))
            await utils.room_check(ctx)

        elif args[0] == "stalk":
            try:
                converter = commands.MemberConverter()
                target_member = await converter.convert(ctx=ctx, argument=" ".join(args[1:]))
            except commands.errors.BadArgument:
                await ctx.send(utils.fill_message("member_not_found", user=ctx.author.id))
                return

            await ctx.send(karma.karma_get(ctx.author, target_member))
            await utils.room_check(ctx)

        elif args[0] == "get":
            try:
                await karma.emoji_get_value(ctx.message)
                await utils.room_check(ctx)
            except discord.errors.Forbidden:
                return

        elif args[0] == "revote":
            if ctx.message.channel.id == config.channel_vote or ctx.author.id == config.admin_id:
                try:
                    await ctx.message.delete()
                    await karma.emoji_revote_value(ctx.message)
                except discord.errors.Forbidden:
                    return
            else:
                await ctx.send(
                    utils.fill_message(
                        "vote_room_only",
                        room=discord.utils.get(ctx.guild.channels, id=config.channel_vote),
                    )
                )

        elif args[0] == "vote":
            if ctx.message.channel.id == config.channel_vote or ctx.author.id == config.admin_id:
                try:
                    await ctx.message.delete()
                    await karma.emoji_vote_value(ctx.message)
                except discord.errors.Forbidden:
                    return
            else:
                await ctx.send(
                    utils.fill_message(
                        "vote_room_only",
                        room=discord.utils.get(ctx.guild.channels, id=config.channel_vote),
                    )
                )

        elif args[0] == "give":
            if ctx.author.id == config.admin_id:
                await karma.karma_give(ctx.message)
            else:
                await ctx.send(utils.fill_message("insufficient_rights", user=ctx.author.id))

        elif args[0] == "message":
            # TODO On embed creation, use Embed(..., url=...) to link to the message
            try:
                converter = commands.MessageConverter()
                target_message = await converter.convert(ctx=ctx, argument=" ".join(args[1:]))
            except commands.errors.BadArgument:
                await ctx.send(utils.fill_message("karma_message_format", user=ctx.author.id))
                return
            await karma.message_karma(ctx, target_message)
        else:
            await ctx.send(utils.fill_message("karma_invalid_command", user=ctx.author.id))

    @commands.cooldown(rate=2, per=30.0, type=commands.BucketType.user)
    @commands.command()
    async def leaderboard(self, ctx, start=1):
        if not 0 < start < 100000000:  # Any value larger than the server
            # user cnt and lower than 32bit
            # int max will do
            await ctx.send(utils.fill_message("karma_lederboard_offser_error", user=ctx.author.id))
            return
        await self.karma.leaderboard(ctx.message.channel, "get", "DESC", start)
        await utils.room_check(ctx)

    @commands.cooldown(rate=2, per=30.0, type=commands.BucketType.user)
    @commands.command()
    async def bajkarboard(self, ctx, start=1):
        if not 0 < start < 100000000:  # Any value larger than the server
            # user cnt and lower than 32bit
            # int max will do
            await ctx.send(utils.fill_message("karma_lederboard_offser_error", user=ctx.author.id))
            return
        await self.karma.leaderboard(ctx.message.channel, "get", "ASC", start)
        await utils.room_check(ctx)

    @commands.cooldown(rate=2, per=30.0, type=commands.BucketType.user)
    @commands.command()
    async def givingboard(self, ctx, start=1):
        if not 0 < start < 100000000:  # Any value larger than the server
            # user cnt and lower than 32bit
            # int max will do
            await ctx.send(utils.fill_message("karma_lederboard_offser_error", user=ctx.author.id))
            return
        await self.karma.leaderboard(ctx.message.channel, "give", "DESC", start)
        await utils.room_check(ctx)

    @commands.cooldown(rate=2, per=30.0, type=commands.BucketType.user)
    @commands.command()
    async def ishaboard(self, ctx, start=1):
        if not 0 < start < 100000000:  # Any value larger than the server
            # user cnt and lower than 32bit
            # int max will do
            await ctx.send(utils.fill_message("karma_lederboard_offser_error", user=ctx.author.id))
            return
        await self.karma.leaderboard(ctx.message.channel, "give", "ASC", start)
        await utils.room_check(ctx)

    @leaderboard.error
    @bajkarboard.error
    @givingboard.error
    @ishaboard.error
    async def leaderboard_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(utils.fill_message("karma_lederboard_offser_error", user=ctx.author.id))


def setup(bot):
    bot.add_cog(Karma(bot))
