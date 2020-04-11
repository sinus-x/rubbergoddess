from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Boolean,
    Date,
    PrimaryKeyConstraint,
    ForeignKey
)
from sqlalchemy.orm import relationship
from repository.database import database


class Review(database.base):
    __tablename__ = 'reviews'

    id          = Column(Integer, primary_key=True)
    discord_id  = Column(BigInteger)
    anonym      = Column(Boolean, default=True)
    subject     = Column(String, ForeignKey("subjects.shortcut",
                     ondelete="CASCADE"))
    tier        = Column(Integer, default=0)
    text_review = Column(String, default=None)
    date        = Column(Date)
    relevance   = relationship('ReviewRelevance')


class ReviewRelevance(database.base):
    __tablename__ = 'review_relevance'
    __table_args__ = (
        PrimaryKeyConstraint('review', 'discord_id', name='key'),
    )

    discord_id = Column(BigInteger)
    vote       = Column(Boolean, default=False)
    review     = Column(Integer, ForeignKey('reviews.id', ondelete="CASCADE"))


class Subject(database.base):
    __tablename__ = 'subjects'

    shortcut = Column(String, primary_key=True)
    reviews = relationship('Review')
