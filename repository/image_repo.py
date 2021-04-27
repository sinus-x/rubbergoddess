from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.image import Image


class ImageRepository(BaseRepository):
    def add_image(self, channel_id: int, message_id: int, attachment_id: int, dhash: str):
        """Add new image hash"""
        if self.get_by_attachment(attachment_id) is not None:
            # attachment already indexed
            return

        session.add(
            Image(
                channel_id=channel_id,
                message_id=message_id,
                attachment_id=attachment_id,
                dhash=dhash,
            )
        )
        session.commit()

    def get_hash(self, dhash: str):
        return session.query(Image).filter(Image.dhash == dhash).all()

    def get_by_message(self, message_id: int):
        return session.query(Image).filter(Image.message_id == message_id).all()

    def get_by_attachment(self, attachment_id: int):
        return session.query(Image).filter(Image.attachment_id == attachment_id).one_or_none()

    def get_all(self):
        return session.query(Image)

    def delete_by_message(self, message_id: int):
        i = session.query(Image).filter(Image.message_id == message_id).delete()
        session.commit()
        return i
