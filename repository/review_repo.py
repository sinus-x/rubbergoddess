import datetime
from typing import List

from sqlalchemy import func, desc

from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.review import Review, ReviewRelevance, Subject, SupervisorReview


class ReviewRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get(self, id: int) -> Review:
        return session.query(Review).filter(Review.id == id).one_or_none()

    def get_subject_reviews(self, subject):
        return (
            session.query(
                Review, func.count(Review.relevance).filter(ReviewRelevance.vote).label("total")
            )
            .filter(Review.subject == subject)
            .outerjoin(Review.relevance)
            .group_by(Review)
            .order_by(desc("total"))
        )

    def get_all_reviews(self):
        return session.query(Review)

    def get_review_by_author_subject(self, author_id, subject) -> Review:
        return (
            session.query(Review)
            .filter(Review.subject == subject, Review.discord_id == str(author_id))
            .first()
        )

    def update_review(self, id, tier, anonym: bool, text) -> Review:
        review = Review(
            id=id, tier=tier, anonym=anonym, text_review=text, date=datetime.date.today()
        )
        session.merge(review)
        session.commit()
        return review

    def add_review(self, author, subject, tier, anonym: bool, text) -> Review:
        try:
            review = Review(
                discord_id=str(author),
                subject=subject,
                tier=tier,
                anonym=anonym,
                text_review=text,
                date=datetime.date.today(),
            )
            session.add(review)
            session.commit()
        except Exception:
            session.rollback()
            raise
        return review

    def remove(self, id):
        session.query(Review).filter(Review.id == id).delete()

    def get_votes_count(self, review_id, vote: bool):
        return (
            session.query(ReviewRelevance)
            .filter(ReviewRelevance.review == review_id, ReviewRelevance.vote == vote)
            .count()
        )

    def get_vote_by_author(self, review_id, author):
        return (
            session.query(ReviewRelevance)
            .filter(ReviewRelevance.review == review_id, ReviewRelevance.discord_id == author)
            .first()
        )

    def add_vote(self, review_id, vote: bool, author):
        relevance = ReviewRelevance(discord_id=author, vote=vote, review=review_id)
        session.merge(relevance)
        session.commit()

    def remove_vote(self, review_id, author):
        session.query(ReviewRelevance).filter(
            ReviewRelevance.review == review_id, ReviewRelevance.discord_id == author
        ).delete()

    def get_subject(self, shortcut):
        # FIXME Outdated, moved to subject_repo.py
        return session.query(Subject).filter(Subject.shortcut == shortcut)

    def add_subject(self, shortcut):
        # FIXME Outdated, moved to subject_repo.py
        subject = Subject(shortcut=shortcut)
        session.merge(subject)
        session.commit()

    # Supervisor

    def get_supervisor_reviews_by_name(self, name: str) -> List[SupervisorReview]:
        """Get reviews for supervisor"""
        return session.query(SupervisorReview).filter(SupervisorReview.name == name).all()

    def get_supervisor_reviews_by_id(self, person_id: int) -> List[SupervisorReview]:
        """Get reviews for supervisor"""
        return session.query(SupervisorReview).filter(SupervisorReview.person_id == person_id).all()

    def add_supervisor_reviews(
        self,
        author: int,
        timestamp: datetime.datetime,
        person_id: int,
        name: str,
        relationship: str,
        thesis_type: str,
        mark_their: str,
        mark_final: str,
        text: str,
    ) -> SupervisorReview:
        result = SupervisorReview(
            discord_id=author,
            timestamp=timestamp,
            person_id=person_id,
            name=name,
            relationship=relationship,
            thesis_type=thesis_type,
            mark_their=mark_their,
            mark_final=mark_final,
            text=text,
        )
        session.merge(result)
        return result
