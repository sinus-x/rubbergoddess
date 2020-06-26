import discord
from discord.ext import commands

from core import check, rubbercog, utils
from repository import review_repo, subject_repo

repo_r = review_repo.ReviewRepository()
repo_s = subject_repo.SubjectRepository()


class Judge(rubbercog.Rubbercog):
    """Subject reviews"""

    def __init__(self, bot):
        super().__init__(bot)

    ##
    ## Commands
    ##

    @commands.cooldown(rate=5, per=60, type=commands.BucketType.user)
    @commands.check(check.is_native)
    @commands.group(name="review")
    async def review(self, ctx):
        """Manage your subject reviews"""
        await utils.send_help(ctx)

    @review.command(name="subject", aliases=["see"])
    async def review_subject(self, ctx, subject: str):
        """See subject's reviews"""
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.send("that is not valid subject")

        name = db_subject.name if db_subject.name is not None else discord.Embed.Empty
        if name is not discord.Embed.Empty and db_subject.category is not None:
            name += f" ({db_subject.category})"

        db_reviews = repo_r.get_subject_reviews(subject)
        if db_reviews.count() == 0:
            embed = self.embed(ctx=ctx, description=name)
            embed.add_field(name="no reviews", value="no one has reviewed this subject yet")
        else:
            review = db_reviews[0].Review
            embed = self.embed(ctx=ctx, description=name, page=(1, db_reviews.count()))
            # TODO Compute average mark
            embed.add_field(name="average mark", value="-1", inline=False)
            # TODO Check if user is anonymous
            embed.add_field(name="Author", value=self.bot.get_user(int(review.discord_id)))
            # TODO Translate
            embed.add_field(name="Mark", value=review.tier)
            # TODO Translate
            embed.add_field(name="Date", value=review.date)

            embed.add_field(name="Text", value=review.text_review, inline=False)

            embed.add_field(name="👍", value=f"{repo_r.get_votes_count(review.id, True)}")
            embed.add_field(name="👎", value=f"{repo_r.get_votes_count(review.id, False)}")

        await ctx.send(embed=embed)

    @review.command(name="add", aliases=["update"])
    async def review_add(self, ctx, subject: str, mark: int, *, text: str):
        """Add a review

        subject: Subject code
        mark: 1-5 (one being best)
        text: Your review
        """
        if mark < 1 or mark > 5:
            return await utils.send_help(ctx)

        if len(text) > 1024:
            return await ctx.send("text too long")

        # check if subject is in database
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.send("that is not valid subject")

        anonymous = isinstance(ctx.channel, discord.DMChannel)
        past_review = repo_r.get_review_by_author_subject(ctx.author.id, subject)

        if past_review is None:
            # add
            repo_r.add_review(ctx.author.id, subject, mark, anonymous, text)
        else:
            # update
            repo_r.update_review(past_review.id, mark, anonymous, text)

        # send confirmation
        await ctx.send("ok.")

    @review.command(name="remove")
    async def review_remove(self, ctx, subject: str):
        """Remove your review

        subject: Subject code
        """
        review = repo_r.get_review_by_author_subject(ctx.author.id, subject)
        if review is None:
            return await ctx.send("no such review")

        repo_r.remove(review.id)
        await ctx.send("review removed.")

    @commands.check(check.is_mod)
    @commands.group(name="sudo_review")
    async def sudo_review(self, ctx):
        """Manage other user's reviews"""
        await utils.send_help(ctx)

    @sudo_review.command(name="remove")
    async def sudo_review_remove(self, ctx, subject: str, user: discord.User):
        """Remove someone's review"""
        pass

    ##
    ## Listeners
    ##

    ##
    ## Logic
    ##

    ##
    ## Helper functions
    ##

    ##
    ## Error handlers
    ##


def setup(bot):
    bot.add_cog(Judge(bot))
