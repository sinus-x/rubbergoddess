from typing import List, Tuple

from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.interactions import Interaction


class InteractionRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def add(
        self,
        guild_id: int,
        action: str,
        giver: int,
        receiver: int,
    ) -> Interaction:
        result = (
            session.query(Interaction)
            .filter(
                Interaction.guild_id == guild_id,
                Interaction.name == action,
                Interaction.giver == giver,
                Interaction.receiver == receiver,
            )
            .one_or_none()
        )

        if result is not None:
            result.count += 1
            session.commit()
            return result

        result = Interaction(
            guild_id=guild_id,
            name=action,
            giver=giver,
            receiver=receiver,
            count=1,
        )
        session.add(result)
        session.commit()
        return result

    # Filters by channel

    def get_guild(self, guild_id: int) -> List[Interaction]:
        return session.query(Interaction).filter(Interaction.guild_id == guild_id).all()

    # Filters by action
    def get_action(self, action: str) -> List[Interaction]:
        return session.query(Interaction).filter(Interaction.name == action).all()

    # Filters by user

    def get_user_action(self, user_id: int, guild_id: int, action: str) -> Tuple[int, int]:
        user = session.query(Interaction).filter(
            Interaction.name == action, Interaction.guild_id == guild_id
        )
        return (
            user.filter(Interaction.giver == user_id).count(),
            user.filter(Interaction.receiver == user_id).count(),
        )

    # Mover module

    def move_user(self, before_id: int, after_id: int) -> int:
        """Replace old user IDs with new one.

        Returns
        -------
        `int`: number of altered interactions
        """
        interactions = session.query(Interaction).all()
        counter = 0
        for interaction in interactions:
            if interaction.giver == before_id:
                interaction.giver == after_id
                counter += 1
            if interaction.receiver == before_id:
                interaction.receiver == after_id
                counter += 1
        session.commit()
        return counter
