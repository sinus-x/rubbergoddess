from sqlalchemy import Column, Integer, BigInteger
from repository.database import database


class Meme(database.base):
    __tablename__ = "meme"

    # fmt: off
    id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(BigInteger)
    guild_id       = Column(BigInteger)
    hugs_gave      = Column(Integer, default=0)
    hugs_recv      = Column(Integer, default=0)
    pets_gave      = Column(Integer, default=0)
    pets_recv      = Column(Integer, default=0)
    hyperpets_gave = Column(Integer, default=0)
    hyperpets_recv = Column(Integer, default=0)
    slaps_gave     = Column(Integer, default=0)
    slaps_recv     = Column(Integer, default=0)
    # fmt: on

    def __repr__(self):
        return (
            f"<User {self.user_id}: "
            "hugs {self.hugs_gave}:{self.hugs_recv} "
            "pets {self.hugs_gave}:{self.hugs_recv} "
            "hyperpets {self.hugs_gave}:{self.hugs_recv} "
            "slaps {self.hugs_gave}:{self.hugs_recv}>"
        )

    def __str__(self):
        return (
            f"User {self.user_id}: "
            "hugs {self.hugs_gave}:{self.hugs_recv}, "
            "pets {self.hugs_gave}:{self.hugs_recv}, "
            "hyperpets {self.hugs_gave}:{self.hugs_recv}, "
            "slaps {self.hugs_gave}:{self.hugs_recv}."
        )
