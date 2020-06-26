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

    def add(self, shortcut: str, name: str, category: str):
        subject = Subject(shortcut=shortcut, name=name, category=category)
        session.merge(subject)
        session.commit()

    def update(self, shortcut: str, *, name: str = None, category: str = None):
        subject = session.query(Subject).filter(Subject.shortcut == shortcut).one_or_none()
        subject.name = name or subject.name
        subject.category = category or subject.category
        session.commit()

    def remove(self, shortcut: str):
        session.query(Subject).filter(Subject.shortcut == shortcut).delete()
