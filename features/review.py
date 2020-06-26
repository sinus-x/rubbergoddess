import discord
from datetime import datetime
from discord.ext.commands import Bot

from core.config import config
from features.base_feature import BaseFeature
from repository import review_repo

review_r = review_repo.ReviewRepository()


class Review(BaseFeature):
    def __init__(self, bot: Bot):
        super().__init__(bot)

    def add_vote(self, review_id, vote: bool, author):
        relevance = review_r.get_vote_by_author(review_id, author)
        if not relevance or relevance.vote != vote:
            review_r.add_vote(review_id, vote, author)

    def add_subject(self, subject):
        review_r.add_subject(subject)

    def remove_subject(self, subject):
        review_r.get_subject(subject).delete()
