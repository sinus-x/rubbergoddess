import discord
from discord.ext import commands

from core.config import config
from core import check, rubbercog, utils
from config.messages import Messages as messages
from features import review


class Review(rubbercog.Rubbercog):
    """Subject reviews"""

    def __init__(self, bot):
        super().__init__(bot)
        self.rev = review.Review(bot)

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.user)
    @commands.check(check.is_mod)
    @commands.command()
    async def db_subject(self, ctx, subcommand=None, subject=None):
        if not subcommand or not subject:
            await ctx.send(messages.subject_format)
            return
        subject = subject.lower()
        if subcommand == "add":
            self.rev.add_subject(subject)
            await ctx.send(f"Zkratka {subject} byla přidána")
            # TODO Add to config, too
        elif subcommand == "remove":
            self.rev.remove_subject(subject)
            await ctx.send(f"Zkratka {subject} byla odebrána")
            await self.event.sudo(ctx.author, ctx.channel, f"Subject {subject} added")
            # TODO Remove from config, too
        else:
            await ctx.send(messages.review_wrong_subject)
            await self.event.sudo(ctx.author, ctx.channel, f"Subject {subject} removed")


def setup(bot):
    bot.add_cog(Review(bot))
