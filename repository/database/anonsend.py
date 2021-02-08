from sqlalchemy import Column, BigInteger, Integer, String
from repository.database import database


class AnonsendChannel(database.base):
    __tablename__ = "anonsend_channels"

    # fmt: off
    id         = Column(Integer, primary_key=True)
    guild_id   = Column(BigInteger)
    channel_id = Column(BigInteger)
    name       = Column(String)
    count      = Column(Integer)
    # fmt: on

    def __str__(self):
        return f"Channel {self.channel_id} in guild {self.guild_id}: {self.name} ({self.count})"

    def __repr__(self):
        return (
            "<AnonsendChannel "
            f"guild_id={self.guild_id} "
            f"channel_id={self.channel_id} "
            f"name={self.name} "
            f"count={self.count}"
            ">"
        )
