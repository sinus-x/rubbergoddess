import datetime

from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.image import Image


class ImageRepository(BaseRepository):
    def add_image(self, channel_id: int, message_id: int, attachment_id: int, dhash: str):
        """Add new image hash"""
        if self.getByAttachment(attachment_id) is not None:
            # attachment already indexed
            return

        session.add(
            Image(
                channel_id=channel_id,
                message_id=message_id,
                attachment_id=attachment_id,
                dhash=dhash,
                timestamp=datetime.datetime.now().replace(microsecond=0),
            )
        )
        session.commit()

    def getHash(self, dhash: str):
        return session.query(Image).filter(Image.dhash == dhash).all()

    def getByAttachment(self, attachment_id: int):
        return session.query(Image).filter(Image.attachment_id == attachment_id).one_or_none()

    def getAll(self):
        return session.query(Image)

    def deleteByMessage(self, message_id: int):
        i = session.query(Image).filter(Image.message_id == message_id).delete()
        session.commit()
        return i
