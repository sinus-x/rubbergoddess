from sqlalchemy import Column, BigInteger, Integer
from repository.database import database


class Points(database.base):
    __tablename__ = "points"

    # fmt: off
    user_id = Column(BigInteger, primary_key=True)
    points  = Column(Integer)
    # fmt: on
