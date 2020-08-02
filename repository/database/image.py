from sqlalchemy import Column, String, BigInteger
from repository.database import database


class Image(database.base):
    __tablename__ = "images"

    # fmt: off
    attachment_id = Column(BigInteger, primary_key=True)
    message_id    = Column(BigInteger)
    channel_id    = Column(BigInteger)
    dhash         = Column(String)
    # fmt: on
