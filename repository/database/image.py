from sqlalchemy import Column, String, BigInteger
from repository.database import database

class Image(database.base):
    __tablename__ = 'images'

    channel    = Column(BigInteger)
    message    = Column(BigInteger)
    discord_id = Column(BigInteger)
    dhash      = Column(String)
