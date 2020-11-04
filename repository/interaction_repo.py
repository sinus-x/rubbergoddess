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
        channel_id: int,
        message_id: int,
        action: str,
        giver: int,
        receiver: int,
    ) -> Interaction:
        result = Interaction(
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=message_id,
            name=action,
            giver=giver,
            receiver=receiver,
        )
        session.add(result)
        return result

    # Filters by channel

    def get_channel(self, channel_id: int) -> List[Interaction]:
        return session.filter(Interaction.channel_id == channel_id).all()

    def get_guild(self, guild_id: int) -> List[Interaction]:
        return session.filter(Interaction.guild_id == guild_id).all()

    # Filters by action
    def get_action(self, action: str) -> List[Interaction]:
        return session.query(Interaction).filter(Interaction.name == action).all()

    # Filters by user

    def get_user_action(self, user_id: int, action: str) -> Tuple[int, int]:
        user = session.query(Interaction).filter(Interaction.name == action)
        return (
            user.filter(Interaction.giver == user_id).count(),
            user.filter(Interaction.receiver == user_id).count(),
        )
