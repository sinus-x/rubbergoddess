from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.verification import User

from datetime import datetime


def time() -> str:
    return datetime.today().strftime("%Y-%m-%d %H:%M:%S")


class UserRepository(BaseRepository):
    # unknown - pending - verified - kicked - banned - quarantined

    def add(self, discord_id: int, login: str, group: str, code: str, status: str = "pending"):
        """Add new user"""
        session.add(
            User(
                discord_id=discord_id,
                login=login,
                group=group,
                code=code,
                status=status,
                changed=time(),
            )
        )
        session.commit()

    def save_verified(self, discord_id: int):
        """Insert login with discord name into database"""
        session.query(User).filter(User.discord_id == discord_id).update(
            {User.status: "verified", User.changed: time()}
        )
        session.commit()

    def update(
        self,
        discord_id: int,
        *,
        login: str = None,
        group: str = None,
        code: str = None,
        status: str = None,
        comment: str = None,
    ):
        """Update user entry"""
        user = session.query(User).filter(User.discord_id == discord_id).one()
        user.login = login or user.login
        user.group = group or user.group
        user.code = code or user.code
        user.status = status or user.status
        user.comment = comment or user.comment
        user.changed = time()
        session.commit()

    def is_not_verified(self, discord_id: int):
        """Check if there's a discord_id"""
        unknown = (
            session.query(User)
            .filter(User.discord_id == discord_id, User.status == "unknown")
            .all()
        )
        pending = (
            session.query(User)
            .filter(User.discord_id == discord_id, User.status == "pending")
            .all()
        )
        return len(unknown) > 0 or len(pending) > 0

    def get(self, discord_id: int):
        """Get user from database"""
        return session.query(User).filter(User.discord_id == discord_id).one_or_none()

    def getByLogin(self, login: str):
        """Get user from database"""
        return session.query(User).filter(User.login == login).one_or_none()

    def getByPrefix(self, prefix: str):
        """Get users from database"""
        return session.query(User).filter(User.login.startswith(prefix)).all()

    def filterId(self, discord_id: int):
        """Find user in database"""
        users = session.query(User).filter(User.discord_id == discord_id).all()
        return users

    def deleteId(self, discord_id: int) -> int:
        count = session.query(User).filter(User.discord_id == discord_id).delete()
        session.commit()
        return count

    def filterLogin(self, login: str):
        return session.query(User).filter(User.login == login).all()

    def filterStatus(self, status: str):
        return session.query(User).filter(User.status == status).all()

    def filterGroup(self, group: str):
        return session.query(User).filter(User.group == group).all()

    def countStatus(self, status: str):
        return session.query(User).filter(User.status == status).count()

    def countGroup(self, group: str):
        return session.query(User).filter(User.group == group).count()
