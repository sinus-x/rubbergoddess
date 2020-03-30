from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.verification import User

from datetime import date

class UserRepository(BaseRepository):
    # unknown - pending - verified - kicked - banned

    def add_user(self, login: str, group: str = "GUEST", status: str = "unknown",
        discord_id: str = "", comment: str = ""):
        """Add new user"""
        session.add(User(login=login, group=group, status=status,
            comment=comment, discord_id=discord_id))
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
        user.changed = date.today().strftime("%Y%m%d")
        session.commit()

    def save_verified(self, discord_id: str):
        """Insert login with discord name into database"""
        user = session.query(User).filter(User.discord_id == discord_id).one_or_none()
        user.status = "verified"
        user.comment = ""
        user.changed = date.today().strftime("%Y%m%d")
        session.commit()

    def update_status(self, login: str, status: str, comment: str):
        """Update status"""
        user = session.query(User).filter(User.login == login).one_or_none()
        user.status = status
        user.comment = comment
        user.changed = date.today().strftime("%Y%m%d")
        session.commit()

    def has_unverified_login(self, login: str):
        """Check if there's a login """
        #FIXME does not seem to be used anywhere
        query = session.query(User).filter(
            User.login == login, User.status == 0).one_or_none()
        return True if query is not None else False

    def get_user(self, login: str = None, discord_id: str = None):
        """Find login from database"""
        if login:
            user = session.query(User).filter(User.login == login).one_or_none()
        elif discord_id:
            user = session.query(User).filter(User.discord_id == discord_id).one_or_none()
        else:
            return
        return user
