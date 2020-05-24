from sqlalchemy import Column, String, Integer, BigInteger
from repository.database import database


class Karma(database.base):
    __tablename__ = "user_karma"

    # fmt: off
    discord_id = Column(BigInteger, primary_key=True)
    karma      = Column(Integer,    default=0)
    positive   = Column(Integer,    default=0)
    negative   = Column(Integer,    default=0)
    # fmt: on


class Karma_emoji(database.base):
    __tablename__ = "emote_karma"

    # fmt: off
    emoji_ID = Column(String,  primary_key=True)
    value    = Column(Integer, default=0)
    # fmt: on
