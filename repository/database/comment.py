from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, Integer, String
from repository.database import database, session


class Comment(database.base):
    """User comment"""

    __tablename__ = "comments"

    id: int = Column(Integer, primary_key=True)
    guild_id: int = Column(BigInteger)
    author_id: int = Column(BigInteger)
    user_id: int = Column(BigInteger)
    text: str = Column(String)
    timestamp: datetime = Column(DateTime)

    @staticmethod
    def add(guild_id: int, author_id: int, user_id: int, text: str):
        """Add user comment"""
        query = Comment(
            guild_id=guild_id,
            author_id=author_id,
            user_id=user_id,
            text=text,
            timestamp=datetime.now(),
        )
        session.add(query)
        session.commit()
        return query

    @staticmethod
    def remove(guild_id: int, id: int):
        """Remove user comment."""
        result = session.query(Comment).filter_by(guild_id=guild_id, id=id).delete()
        session.commit()
        return result > 0

    @staticmethod
    def get(guild_id: int, user_id: int):
        """Get user comments."""
        return session.query(Comment).filter_by(guild_id=guild_id, user_id=user_id).all()

    def __str__(self):
        return f"Comment about {self.user_id}: {self.text}"

    def __repr__(self):
        return (
            "<Comment "
            f"id={self.id} "
            f"guild_id={self.guild_id} "
            f"author_id={self.author_id} "
            f"user_id={self.user_id} "
            f'text="{self.text}" '
            f'timestamp="{self.timestamp}"'
            ">"
        )
