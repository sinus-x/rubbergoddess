from sqlalchemy import Column, Integer, BigInteger, String
from repository.database import database


class Interaction(database.base):
    __tablename__ = "interactions"

    # fmt: off
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String)
    guild_id   = Column(BigInteger)
    giver      = Column(BigInteger)
    receiver   = Column(BigInteger)
    count      = Column(Integer)
    # fmt: on

    def __repr__(self):
        return (
            f"<Interaction name={self.name} guild_id={self.guild_id} "
            f"giver={self.giver} receiver={self.receiver} count={self.count}>"
        )

    def __str__(self):
        return (
            f"{self.name} between {self.giver} and {self.receiver} "
            f"in {self.guild_id}: {self.count}."
        )

    def __hash__(self):
        return hash(self.name + str(self.giver) + str(self.receiver))
