import discord
from discord.ext import commands

from cogs.resource import CogText
from core import acl, rubbercog, utils
from repository import review_repo, subject_repo

repo_r = review_repo.ReviewRepository()
repo_s = subject_repo.SubjectRepository()


class Review(rubbercog.Rubbercog):
    """Subject reviews"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("review")

    ##
    ## Commands
    ##

    @commands.cooldown(rate=5, per=60, type=commands.BucketType.user)
    @commands.check(acl.check)
    @commands.group(name="review")
    async def review(self, ctx):
        """Manage your subject reviews"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @review.command(name="subject", aliases=["see"])
    async def review_subject(self, ctx, subject: str):
        """See subject's reviews"""
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.reply(self.text.get("no_subject"))

        title = self.text.get("embed", "title") + subject
        name = db_subject.name if db_subject.name is not None else discord.Embed.Empty
        if name is not discord.Embed.Empty and db_subject.category is not None:
            name += f" ({db_subject.category})"

        db_reviews = repo_r.get_subject_reviews(subject)
        if db_reviews.count() == 0:
            return await ctx.reply(self.text.get("no_reviews"))

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

    @commands.check(acl.check)
    @review.command(name="list", aliases=["available"])
    async def review_list(self, ctx):
        """Get list of reviewed subjects"""
        subjects = set()
        for r in repo_r.get_all_reviews():
            subjects.add(r.subject)

        if not len(subjects):
            return await ctx.reply(self.text.get("empty"))

        await ctx.reply(">>> " + ", ".join(f"`{s}`" for s in sorted(subjects)))

    @commands.check(acl.check)
    @review.command(name="my-list")
    async def review_mylist(self, ctx):
        """Get list of your reviewed subjects"""
        subjects = set()
        for r in repo_r.get_all_reviews():
            if r.discord_id == ctx.author.id:
                subjects.add(r.subject)

        if not len(subjects):
            return await ctx.reply(self.text.get("empty"))

        await ctx.reply(">>> " + ", ".join(f"`{s}`" for s in sorted(subjects)))

    @commands.check(acl.check)
    @review.command(name="add", aliases=["update"])
    async def review_add(self, ctx, subject: str, mark: int, *, text: str):
        """Add a review

        subject: Subject code
        mark: 1-5 (one being best)
        text: Your review
        """
        result = await self.add_review(ctx, subject, mark, text, anonymous=False)

        if result is not None:
            await self.event.user(ctx, f"Review **#{result.id}** for **{subject}**.")
            await ctx.reply(self.text.get("added"))

    @commands.check(acl.check)
    @review.command(name="add-anonymous", aliases=["anonymous", "anon"])
    async def review_add_anonymous(self, ctx, subject: str, mark: int, *, text: str):
        """Add anonymous review

        subject: Subject code
        mark: 1-5 (one being best)
        text: Your review
        """
        result = await self.add_review(ctx, subject, mark, text, anonymous=True)

        if result is not None:
            await utils.delete(ctx.message)
            await self.event.user(ctx, f"Anonymous review **#{result.id}** for **{subject}**.")
            await ctx.send(self.text.get("added"))

    @commands.check(acl.check)
    @review.command(name="remove")
    async def review_remove(self, ctx, subject: str):
        """Remove your review

        subject: Subject code
        """
        review = repo_r.get_review_by_author_subject(ctx.author.id, subject)
        if review is None:
            return await ctx.send(self.text.get("no_review", mention=ctx.author.mention))

        repo_r.remove(review.id)
        await self.event.user(ctx, f"Removed review for **{subject}**.")
        return await ctx.reply(self.text.get("removed"))

    @commands.check(acl.check)
    @commands.group(name="sudo_review")
    async def sudo_review(self, ctx):
        """Manage other user's reviews"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @sudo_review.command(name="remove")
    async def sudo_review_remove(self, ctx, id: int):
        """Remove someone's review"""
        db_review = repo_r.get(id)
        if db_review is None:
            return await ctx.send(self.text.get("no_review", mention=ctx.author.mention))

        repo_r.remove(id)
        await self.event.sudo(ctx, f"Review **#{id}** removed")
        return await ctx.reply(self.text.get("removed"))

    @commands.check(acl.check)
    @commands.group(name="subject")
    async def subject(self, ctx):
        """Manage subjects"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @subject.command(name="info")
    async def subject_info(self, ctx, subject: str):
        """Get information about subject

        subject: Subject code
        """
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.send(self.text.get("no_subject"))

        embed = self.embed(ctx=ctx, title=db_subject.shortcut)
        if db_subject.name or db_subject.category:
            embed.add_field(
                name=db_subject.name or "\u200b",
                value=db_subject.category or "\u200b",
                inline=False,
            )
        embed.add_field(
            name=self.text.get("info", "reviews"),
            value=self.text.get("info", "count", count=len(db_subject.reviews), subject=subject)
            if len(db_subject.reviews)
            else self.text.get("info", "none"),
            inline=False,
        )

        await ctx.reply(embed=embed)

    @commands.check(acl.check)
    @subject.command(name="add")
    async def subject_add(self, ctx, subject: str, name: str, category: str):
        """Add subject

        subject: Subject code
        name: Subject name
        category: Subject faculty or other assignment
        """
        db_subject = repo_s.get(subject)
        if db_subject is not None:
            return await ctx.reply(self.text.get("subject_exists"))

        repo_s.add(subject, name, category)
        await self.event.sudo(ctx, f"Subject **{subject}** added.")
        await ctx.reply(self.text.get("subject_added"))

    @commands.check(acl.check)
    @subject.command(name="update")
    async def subject_update(self, ctx, subject: str, name: str, category: str):
        """Update subject

        subject: Subject code
        name: Subject name
        category: Subject faculty or other assignment
        """
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.reply(self.text.get("no_subject"))

        repo_s.update(subject, name=name, category=category)
        await self.event.sudo(ctx, f"Subject **{subject}** updated.")
        await ctx.reply(self.text.get("subject_updated"))

    @commands.check(acl.check)
    @subject.command(name="remove")
    async def subject_remove(self, ctx, subject: str):
        """Remove subject

        subject: Subject code
        """
        db_subject = repo_s.get(subject)
        if db_subject is None:
            return await ctx.reply(self.text.get("no_subject"))

        repo_s.remove(subject)
        await self.event.sudo(ctx, f"Subject **{subject}** removed.")
        await ctx.reply(self.text.get("subject_removed"))

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
            or not reaction.message.embeds[0].title.startswith(self.text.get("embed", "title"))
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
        subject = embed.title.replace(self.text.get("embed", "title"), "")
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
        else:
            page = 0

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
        except Exception:
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
        name = self.bot.get_user(int(review.discord_id)) or self.text.get("embed", "no_user")
        if review.anonym:
            name = self.text.get("embed", "anonymous")

        embed.add_field(inline=False,
            name=self.text.get("embed", "num", num=str(review.id)),
            value=self.text.get("embed", "average", num=f"{average:.1f}"),
        )
        embed.add_field(
            name=name,
            value=review.date
        )
        embed.add_field(
            name=self.text.get("embed", "mark"),
            value=review.tier
        )

        text: str = review.text_review
        n: int = 1024
        text_pages: str = [(text[i:i+n]) for i in range(0, len(text), n)]
        for i, page in enumerate(text_pages):
            embed.add_field(
                inline=False,
                name=self.text.get("embed", "text") if i == 0 else "\u200b",
                value=page,
            )
        # fmt: on

        embed.add_field(name="👍", value=f"{repo_r.get_votes_count(review.id, True)}")
        embed.add_field(name="👎", value=f"{repo_r.get_votes_count(review.id, False)}")

        return embed

    async def add_review(self, ctx, subject: str, mark: int, text: str, anonymous: bool):
        """Add and return review"""
        if mark < 1 or mark > 5:
            return await ctx.send(self.text.get("wrong_mark"))

        # check if subject is in database
        db_subject = repo_s.get(subject)
        if db_subject is None:
            await ctx.send(self.text.get("no_subject"))
            return

        if text is None or not len(text):
            await ctx.send(self.text.get("no_text"))
            return

        past_review = repo_r.get_review_by_author_subject(ctx.author.id, subject)

        if past_review is None:
            # add
            result = repo_r.add_review(ctx.author.id, subject, mark, anonymous, text)
        else:
            # update
            result = repo_r.update_review(past_review.id, mark, anonymous, text)

        return result
