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


class SupervisorReview(database.base):
    __tablename__ = "reviews_supervisors"

    # fmt: off
    id           = Column(Integer, primary_key=True)
    discord_id   = Column(BigInteger)
    timestamp    = Column(Date)
    person_id    = Column(Integer)
    name         = Column(String)
    relationship = Column(String)
    thesis_type  = Column(String)
    mark_their   = Column(String)
    mark_final   = Column(String)
    text         = Column(String)
    # fmt: on

    def __str__(self):
        return f"Supervisor review by {self.discord_id}: {self.text}."

    def __repr__(self):
        attrs = (
            ("content_type", self.content_type),
            ("discord_id", self.discord_id),
            ("timestamp", self.timestamp),
            ("person_id", self.person_id),
            ("name", self.name),
            ("relationship", self.relationship),
            ("thesis_type", self.thesis_type),
            ("mark_their", self.mark_their),
            ("mark_final", self.mark_final),
            ("text", self.text),
        )
        return "<%s %s>" % (
            self.__class__.__name__,
            " ".join("%s=%r" % a for a in attrs),
        )


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
        return f"<Subject shortcut={self.shortcut} name={self.name} category={self.category}>"

    def __str__(self):
        return self.__repr__()
