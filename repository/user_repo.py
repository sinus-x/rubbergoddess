from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.verification import User

from datetime import datetime

class UserRepository(BaseRepository):
    # unknown - pending - verified - kicked - banned

    def add_user(self, discord_id: str = "", login: str = "xlogin00",
        group: str = "GUEST", status: str = "unknown", code: str = "NONE",
        comment: str = ""):
        """Add new user"""
        session.add(User(login=login, group=group, status=status,
            comment=comment, discord_id=discord_id, code=code,
            changed=datetime.today().strftime("%Y-%m-%d %H-%M-%S")))
        session.commit()

    def save_code(self, code: str, discord_id: str):
        """Update a specified user with a new verification code"""
        user = session.query(User).filter(User.discord_id == discord_id).one_or_none()
        if not user:
            self.add_user(discord_id)
            user = session.query(User).filter(User.discord_id == discord_id).one_or_none()
        user.code = code
        user.discord_id = discord_id
        user.status = "pending"
        user.comment = ""
        user.changed = datetime.today().strftime("%Y-%m-%d %H-%M-%S")
        session.commit()

    def save_verified(self, discord_id: str):
        """Insert login with discord name into database"""
        user = session.query(User).filter(User.discord_id == discord_id).one_or_none()
        user.status = "verified"
        user.comment = ""
        user.changed = datetime.today().strftime("%Y-%m-%d %H-%M-%S")
        session.commit()

    def update_status(self, discord_id: str, status: str, comment: str = ""):
        """Update status"""
        user = session.query(User).filter(User.discord_id == discord_id).one_or_none()
        user.status = status
        user.comment = comment
        user.changed = datetime.today().strftime("%Y-%m-%d %H-%M-%S")
        session.commit()

    def update_comment(self, discord_id: str, comment: str):
        """Update comment"""
        user = session.query(User).filter(User.discord_id == discord_id).one_or_none()
        user.comment = comment
        user.changed = datetime.today().strftime("%Y-%m-%d %H-%M-%S")
        session.commit()

    def is_not_verified(self, discord_id: str):
        """Check if there's a discord_id"""
        unknown = session.query(User).filter(
            User.discord_id == discord_id, User.status == "unknown").all()
        pending = session.query(User).filter(
            User.discord_id == discord_id, User.status == "pending").all()
        return len(unknown) > 0 or len(pending) > 0

    def get_users (self, discord_id: str = None):
        """Find user in database"""
        users = session.query(User).filter(User.discord_id == discord_id).all()
        return users

    def delete_users (self, discord_id: str = None):
        users = session.query(User).filter(User.discord_id == discord_id).delete()
        session.commit()
        return users
