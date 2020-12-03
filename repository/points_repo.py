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

    def getUsers(self, order: str, limit: int = 10, offset: int = 0):
        if order == "desc":
            order = Points.points.desc()
        elif order == "asc":
            order = Points.points.asc()
        else:
            raise Exception("Invalid order: " + order)
        return session.query(Points).order_by(order).offset(offset).limit(limit)

    # Mover module

    def move_user(self, before_id: int, after_id: int) -> int:
        """Replace old user IDs with new one.

        Returns
        -------
        `int`: number of altered interactions
        """
        user = session.query(Points).filter(Points.user_id == before_id).one_or_none()
        if user is None:
            return 0
        session.query(Points).filter(Points.user_id == after_id).delete()

        user.user_id = after_id
        session.commit()
        return 1
