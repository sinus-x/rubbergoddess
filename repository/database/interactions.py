from sqlalchemy import Column, Integer, BigInteger, String
from repository.database import database


class Interaction(database.base):
    __tablename__ = "interactions"

    # fmt: off
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String)
    guild_id   = Column(BigInteger)
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger)
    giver      = Column(BigInteger)
    receiver   = Column(BigInteger)
    # fmt: on

    def __repr__(self):
        return (
            f"<Interaction {self.name}: "
            f"message_id={self.message_id} "
            f"channel_id={self.channel_id} "
            f"guild_id={self.guild_id} "
            f"giver={self.giver} "
            f"receiver={self.receiver}>"
        )

    def __str__(self):
        return (
            f"{self.name} between {self.giver} and {self.receiver} "
            f"(message {self.message_id} in channel {self.channel_id} in {self.guild_id}."
        )

    def __hash__(self):
        return hash(self.message_id)
