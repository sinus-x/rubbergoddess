from sqlalchemy import Column, Integer, BigInteger, String
from repository.database import database


class Seeking(database.base):
    __tablename__ = "seeking"

    # fmt: off
    id =         Column(Integer, primary_key=True, autoincrement=True)
    user_id =    Column(BigInteger)
    message_id = Column(BigInteger, unique=True)
    channel_id = Column(BigInteger, index=True)
    text =       Column(String)
    # fmt: on
