import discord
from discord.ext import commands

from core import check, rubbercog, utils
from core.text import text
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
            return await ctx.send(text.get("judge", "no subject"))

        title = text.get("judge", "embed_title") + subject
        name = db_subject.name if db_subject.name is not None else discord.Embed.Empty
        if name is not discord.Embed.Empty and db_subject.category is not None:
            name += f" ({db_subject.category})"

        db_reviews = repo_r.get_subject_reviews(subject)
        if db_reviews.count() == 0:
            return await ctx.send(text.fill("judge", "no reviews", mention=ctx.author.mention))

        _total = 0
        for db_review in db_reviews:
            _total += db_review.Review.tier
        average = _total / db_reviews.count()

        review = db_reviews[0].Review
        embed = self.embed(ctx=ctx, title=title, description=name, page=(1, db_reviews.count()))
        embed = self.fill_subject_embed(embed, review, average)

        message = await ctx.send(embed=embed)
        if db_reviews.count() > 1:
            await message.add_reaction("◀")
            await message.add_reaction("▶")
        if db_reviews.count() > 0:
            await message.add_reaction("👍")
            await message.add_reaction("🛑")
            await message.add_reaction("👎")

        await utils.delete(ctx)

    @review.command(name="add", aliases=["update"])
    async def review_add(self, ctx, subject: str, mark: int, *, text: str):
        """Add a review

        subject: Subject code
        mark: 1-5 (one being best)
        text: Your review
        """
        if mark < 1 or mark > 5:
            return await ctx.send(text.get("judge", "wrong mark"))

        if len(text) > 1024:
            return await ctx.send(text.get("judge", "text too long"))

        # check if subject is in database
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.send(text.get("judge", "no subject"))

        anonymous = isinstance(ctx.channel, discord.DMChannel)
        past_review = repo_r.get_review_by_author_subject(ctx.author.id, subject)

        if past_review is None:
            # add
            repo_r.add_review(ctx.author.id, subject, mark, anonymous, text)
        else:
            # update
            repo_r.update_review(past_review.id, mark, anonymous, text)

        # send confirmation
        await self.event.user(ctx, f"Review by {ctx.author} for {subject} added")
        return await ctx.send(text.get("judge", "added"))

    @review.command(name="remove")
    async def review_remove(self, ctx, subject: str):
        """Remove your review

        subject: Subject code
        """
        review = repo_r.get_review_by_author_subject(ctx.author.id, subject)
        if review is None:
            return await ctx.send(text.fill("judge", "no review", mention=ctx.author.mention))

        repo_r.remove(review.id)
        await self.event.user(ctx, f"Review by {ctx.author} for {subject} removed")
        return await ctx.send(text.get("judge", "removed"))

    @commands.check(check.is_mod)
    @commands.group(name="sudo_review")
    async def sudo_review(self, ctx):
        """Manage other user's reviews"""
        await utils.send_help(ctx)

    @sudo_review.command(name="remove")
    async def sudo_review_remove(self, ctx, id: int):
        """Remove someone's review"""
        db_review = repo_r.get(id)
        if db_review is None:
            return await ctx.send(text.fill("judge", "no review", mention=ctx.author.mention))

        repo_r.remove(id)
        await self.event.sudo(ctx, f"Review {id} removed")
        return await ctx.send(text.get("judge", "removed"))

    @commands.check(check.is_mod)
    @commands.group(name="sudo_subject")
    async def sudo_subject(self, ctx):
        """Manage subjects"""
        await utils.send_help(ctx)

    @sudo_subject.command(name="add")
    async def sudo_subject_add(self, ctx, subject: str, name: str, category: str):
        """Add subject

        subject: Subject code
        name: Subject name
        category: Subject faculty or other assignment
        """
        db_subject = repo_s.get(subject)
        if db_subject is not None:
            return await ctx.send(text.get("judge", "subject exists"))

        repo_s.add(subject, name, category)
        await self.event.sudo(ctx, f"Subject {subject} added")
        await ctx.send(text.get("judge", "subject added"))

    @sudo_subject.command(name="update")
    async def sudo_subject_update(self, ctx, subject: str, name: str, category: str):
        """Update subject

        subject: Subject code
        name: Subject name
        category: Subject faculty or other assignment
        """
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.send(text.get("judge", "no subject"))

        repo_s.update(subject, name, category)
        await self.event.sudo(ctx, f"Subject {subject} updated")
        await ctx.send(text.get("judge", "subject updated"))

    @sudo_subject.command(name="remove")
    async def sudo_subject_remove(self, ctx, subject: str):
        """Remove subject

        subject: Subject code
        """
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.send(text.get("judge", "no subject"))

        repo_s.remove(subject)
        await self.event.sudo(ctx, f"Subject {subject} removed")
        await ctx.send(text.get("judge", "subject removed"))

    ##
    ## Listeners
    ##
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # check for wanted embed
        if (
            user.bot
            or len(reaction.message.embeds) != 1
            or not isinstance(reaction.message.embeds[0].title, str)
            or not reaction.message.embeds[0].title.startswith(text.get("judge", "embed_title"))
        ):
            return

        scroll = False
        vote = False
        scroll_delta = 0
        vote_value = 0

        # check for scroll availability
        if hasattr(reaction, "emoji"):
            # scrolling
            if str(reaction.emoji) == "◀":
                scroll = True
                scroll_delta = -1
            elif str(reaction.emoji) == "▶":
                scroll = True
                scroll_delta = 1
            # voting
            elif str(reaction.emoji) == "👍":
                vote = True
                vote_value = 1
            elif str(reaction.emoji) == "🛑":
                vote = True
                vote_value = 0
            elif str(reaction.emoji) == "👎":
                vote = True
                vote_value = -1
            # invalid
            else:
                # invalid reaction
                return await self._remove_reaction(reaction, user)
        else:
            # invalid reaction
            return await self._remove_reaction(reaction, user)

        embed = reaction.message.embeds[0]
        if embed.footer == discord.Embed.Empty or " | " not in embed.footer.text:
            return await self._remove_reaction(reaction, user)

        # get reviews for given subject
        subject = embed.title.replace(text.get("judge", "embed_title"), "")
        reviews = repo_r.get_subject_reviews(subject)

        _total = 0
        for review in reviews:
            _total += review.Review.tier
        average = _total / reviews.count()

        # get page
        footer_text = embed.footer.text
        if scroll:
            pages = footer_text.split(" | ")[-1]
            page_current = int(pages.split("/")[0]) - 1

            page = (page_current + scroll_delta) % reviews.count()
            footer_text = footer_text.replace(pages, f"{page+1}/{reviews.count()}")

        # get new review
        review = reviews[page].Review

        if vote:
            # apply vote
            if user.id == review.discord_id:
                return await self._remove_reaction(reaction, user)
            if vote_value == 0:
                repo_r.remove_vote(review.id, str(user.id))
            else:
                repo_r.add_vote(review.id, vote_value == 1, str(user.id))

        # update embed
        embed = self.fill_subject_embed(embed, review, average)
        embed.set_footer(text=footer_text, icon_url=embed.footer.icon_url)
        await reaction.message.edit(embed=embed)

        await self._remove_reaction(reaction, user)

    ##
    ## Helper functions
    ##
    async def _remove_reaction(self, reaction, user):
        try:
            await reaction.remove(user)
        except:
            pass

    ##
    ## Logic
    ##
    def fill_subject_embed(
        self, embed: discord.Embed, review: object, average: float
    ) -> discord.Embed:
        # reset any previous
        embed.clear_fields()

        # add content
        # fmt: off
        name = self.bot.get_user(int(review.discord_id)) or text.get("judge", "embed_no_user")
        if review.anonym:
            name = text.get("judge", "embed_anonymous")

        embed.add_field(inline=False,
            name=text.fill("judge", "embed_no", num=str(review.id)),
            value=text.fill("judge", "embed_average", num=f"{average:.1f}"),
        )
        embed.add_field(name=name, value=review.date)
        embed.add_field(name=text.get("judge", "embed_mark"), value=review.tier)
        embed.add_field(inline=False,
            name=text.get("judge", "embed_text"),
            value=review.text_review,
        )
        # fmt: on

        embed.add_field(name="👍", value=f"{repo_r.get_votes_count(review.id, True)}")
        embed.add_field(name="👎", value=f"{repo_r.get_votes_count(review.id, False)}")

        return embed

    ##
    ## Error handlers
    ##


def setup(bot):
    bot.add_cog(Judge(bot))
