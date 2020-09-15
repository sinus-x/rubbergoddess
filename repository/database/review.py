from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Boolean,
    Date,
    PrimaryKeyConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from repository.database import database


class Review(database.base):
    __tablename__ = "reviews"

    # fmt: off
    id          = Column(Integer, primary_key=True)
    discord_id  = Column(BigInteger)
    anonym      = Column(Boolean, default=True)
    subject     = Column(String,  ForeignKey("subjects.shortcut", ondelete="CASCADE"))
    tier        = Column(Integer, default=0)
    text_review = Column(String,  default=None)
    date        = Column(Date)
    relevance   = relationship('ReviewRelevance')
    # fmt: on


class ReviewRelevance(database.base):
    __tablename__ = "review_relevance"
    __table_args__ = (PrimaryKeyConstraint("review", "discord_id", name="key"),)

    # fmt: off
    discord_id = Column(BigInteger)
    vote       = Column(Boolean, default=False)
    review     = Column(Integer, ForeignKey('reviews.id', ondelete="CASCADE"))
    # fmt: on


class Subject(database.base):
    __tablename__ = "subjects"

    # fmt: off
    shortcut = Column(String, primary_key=True)
    category = Column(String)
    name     = Column(String)
    reviews  = relationship('Review')
    # fmt: on

    def __repr__(self):
        return f"{self.shortcut}: {self.name} ({self.category})"

    def __str__(self):
        return self.__repr__()
