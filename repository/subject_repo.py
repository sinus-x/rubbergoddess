from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.review import Subject


class SubjectRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get(self, shortcut: str):
        return session.query(Subject).filter(Subject.shortcut == shortcut).one_or_none()

    def getAll(self):
        return session.query(Subject).all()

    def add(self, shortcut: str):
        subject = Subject(shortcut=shortcut)
        session.merge(subject)
        session.commit()
