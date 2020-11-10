from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.meme import Meme


class MemeRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get(self, guild_id: int, user_id: int):
        return (
            session.query(Meme)
            .filter(Meme.guild_id == guild_id, Meme.user_id == user_id)
            .one_or_none()
        )

    def hug(self, guild_id: int, giver: int, receiver: int):
        user_g = self.get(guild_id, giver)
        user_r = self.get(guild_id, receiver)

        if user_g is None:
            user_g = session.add(Meme(user_id=giver, guild_id=guild_id, hugs_gave=1))
        else:
            user_g.hugs_gave += 1

        if user_r is None:
            user_r = session.add(Meme(user_id=receiver, guild_id=guild_id, hugs_recv=1))
        else:
            user_r.hugs_recv += 1

        session.commit()

    def pet(self, guild_id: int, giver: int, receiver: int):
        user_g = self.get(guild_id, giver)
        user_r = self.get(guild_id, receiver)

        if user_g is None:
            user_g = session.add(Meme(user_id=giver, guild_id=guild_id, pets_gave=1))
        else:
            user_g.pets_gave += 1

        if user_r is None:
            user_r = session.add(Meme(user_id=receiver, guild_id=guild_id, pets_recv=1))
        else:
            user_r.pets_recv += 1

        session.commit()

    def hyperpet(self, guild_id: int, giver: int, receiver: int):
        user_g = self.get(guild_id, giver)
        user_r = self.get(guild_id, receiver)

        if user_g is None:
            user_g = session.add(Meme(user_id=giver, guild_id=guild_id, hyperpets_gave=1))
        else:
            user_g.hyperpets_gave += 1

        if user_r is None:
            user_r = session.add(Meme(user_id=receiver, guild_id=guild_id, hyperpets_recv=1))
        else:
            user_r.hyperpets_recv += 1

        session.commit()

    def slap(self, guild_id: int, giver: int, receiver: int):
        user_g = self.get(guild_id, giver)
        user_r = self.get(guild_id, receiver)

        if user_g is None:
            user_g = session.add(Meme(user_id=giver, guild_id=guild_id, slaps_gave=1))
        else:
            user_g.slaps_gave += 1

        if user_r is None:
            user_r = session.add(Meme(user_id=receiver, guild_id=guild_id, slaps_recv=1))
        else:
            user_r.slaps_recv += 1

        session.commit()
