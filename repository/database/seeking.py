from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from repository.database import database


class Seeking(database.base):
    __tablename__ = "seeking"

    # fmt: off
    id =         Column(Integer, primary_key=True, autoincrement=True)
    user_id =    Column(BigInteger)
    channel_id = Column(BigInteger)
    text =       Column(String)
    timestamp =  Column(DateTime)
    # fmt: on
