from typing import List, Optional, Union

from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.anonsend import AnonsendChannel


class AnonsendRepository(BaseRepository):
    def add(self, guild_id: int, channel_id: int, name: str) -> AnonsendChannel:
        if self.get(name=name) is not None:
            raise ValueError(f"Name {name} already exists.")

        result = AnonsendChannel(
            guild_id=guild_id,
            channel_id=channel_id,
            name=name,
            count=0,
        )
        session.add(result)
        session.commit()
        return result

    def increment(self, name: str) -> AnonsendChannel:
        result = self.get(name=name)
        result.count += 1
        session.commit()
        return result

    def get(
        self, *, name: str = None, channel_id: int = None
    ) -> Union[Optional[AnonsendChannel], List[AnonsendChannel]]:
        """Get anonsend channels.
        Returns
        -------
        AnonsendChannel, list of them or None.
        """
        if channel_id is None and name is None:
            raise ValueError("`channel_id` or `name` has to be specified.")

        if name is not None:
            return (
                session.query(AnonsendChannel)
                .filter(
                    AnonsendChannel.name == name,
                )
                .one_or_none()
            )

        return (
            session.query(AnonsendChannel)
            .filter(
                AnonsendChannel.channel_id == channel_id,
            )
            .all()
        )

    def get_all(self, guild_id: int) -> List[AnonsendChannel]:
        return (
            session.query(AnonsendChannel)
            .filter(
                AnonsendChannel.guild_id == guild_id,
            )
            .all()
        )

    def rename(self, old_name: int, new_name: str) -> AnonsendChannel:
        result = self.get(name=old_name)

        if result is None:
            raise ValueError(f"Name `{old_name}` does not exist.")
        if self.get(name=new_name) is not None:
            raise ValueError(f"Name `{new_name}` already exists.")

        result.name = new_name
        session.commit()
        return result

    def remove(self, *, channel_id: int = None, name: str = None) -> int:
        """Remove anonsend channels.
        Returns
        -------
        int: Number of deleted entries.
        """
        if channel_id is None and name is None:
            raise ValueError("`channel_id` or `name` has to be specified.")

        if name is not None:
            return (
                session.query(AnonsendChannel)
                .filter(
                    AnonsendChannel.name == name,
                )
                .delete()
            )

        if channel_id is not None:
            return (
                session.query(AnonsendChannel)
                .filter(
                    AnonsendChannel.channel_id == channel_id,
                )
                .delete()
            )
