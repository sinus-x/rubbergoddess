from datetime import datetime
from typing import Optional, List

from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.seeking import Seeking


class SeekingRepository(BaseRepository):
    def add(self, user_id: int, channel_id: int, text: str):
        session.add(
            Seeking(user_id=user_id, channel_id=channel_id, text=text, timestamp=datetime.now())
        )
        session.commit()

    def get(self, item_id: int) -> Optional[Seeking]:
        return session.query(Seeking).filter(Seeking.id == item_id).one_or_none()

    def countAll(self) -> int:
        return session.query(Seeking).count()

    def getAll(self, channel_id: int) -> Optional[List[Seeking]]:
        # return session.query(Seeking).filter(Seeking.channel_id == channel_id).all()
        return session.query(Seeking).all()

    def delete(self, item_id: int) -> int:
        num = session.query(Seeking).filter(Seeking.id == item_id).delete()
        session.commit()
        return num
