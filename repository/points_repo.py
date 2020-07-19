from sqlalchemy import func

from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.points import Points


class PointsRepository(BaseRepository):
    def increment(self, user_id: int, points: int):
        """Add points to user"""
        user = session.query(Points).filter(Points.user_id == user_id).one_or_none()
        if user is None:
            session.add(Points(user_id=user_id, points=points))
        else:
            user.points += points
        session.commit()

    def get(self, user_id: int):
        return session.query(Points).filter(Points.user_id == user_id).one_or_none()

    def getPosition(self, points):
        result = (
            session.query(func.count(Points.user_id))
            .filter(getattr(Points, "points") > points)
            .one_or_none()
        )
        return result[0] + 1 if result else None

    def getAll(self):
        return session.query(Points).all()
