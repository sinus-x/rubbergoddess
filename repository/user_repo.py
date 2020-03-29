from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.verification import Permit, Valid_person

class UserRepository(BaseRepository):
    # 0 ... unknown
    # 1 ... pending
    # 2 ... verified
    # 3 ... kicked
    # 4 ... banned

    def save_sent_code(self, login: str, code: str):
        """Update a specified login with a new verification code"""
        person = session.query(Valid_person).filter(Valid_person.login == login).one_or_none()
        person.code = code
        person.status = 1
        session.commit()

    def save_verified(self, login: str, discord_id: str):
        """Insert login with discord name into database"""
        session.add(Permit(login=login, discord_ID=discord_id))
        person = session.query(Valid_person).filter(Valid_person.login == login).one_or_none()
        person.status = 2
        session.commit()

    def has_unverified_login(self, login: str):
        """Check if there's a login """
        #TODO check twice for FEKT/VUT option
        query = session.query(Valid_person).filter(
            Valid_person.login == login, Valid_person.status == 1).one_or_none()
        return True if query is not None else False

    def get_user(self, login: str, status):
        """Find login from database"""
        #TODO check twice for FEKT/VUT option
        if not status:
            user = session.query(Valid_person).filter(Valid_person.login == login).one_or_none()
        else:
            user = session.query(Valid_person).filter(
                Valid_person.login == login, Valid_person.status == status).one_or_none()
        return user

    def add_user(self, login: str, group: str, status: int = 1):
        #TODO check twice for FEKT/VUT option
        """Find login from database"""
        session.add(Valid_person(login=login, year=group, status=status))
        session.commit()
