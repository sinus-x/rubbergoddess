from sqlalchemy import Column, String, BigInteger, LargeBinary

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class Database:
    def __init__(self):
        self.base = declarative_base()
        self.db = create_engine("sqlite:///data/backup/default.db")


database = Database()
session = sessionmaker(database.db)()


#


def init():
    database.base.metadata.create_all(database.db)
    session.commit()


def wipe():
    database.base.metadata.drop_all(database.db)


class Information(database.base):
    __tablename__ = "information"

    guild_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger)
    author_id = Column(BigInteger)

    @staticmethod
    def get():
        return session.query(Information).one_or_none()

    @staticmethod
    def add(guild_id: int, channel_id: int, author_id: int):
        if Information.get() is not None:
            return

        information = Information(
            guild_id=guild_id,
            channel_id=channel_id,
            author_id=author_id,
        )
        session.add(information)
        session.commit()

    def __repr__(self):
        return (
            f'<Information guild_id="{self.guild_id}" '
            f'channel_id="{self.channel_id}" author_id="{self.author_id}">'
        )


class User(database.base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    avatar = Column(LargeBinary)

    @staticmethod
    def get(user_id: int):
        return (
            session.query(User)
            .filter(
                User.user_id == user_id,
            )
            .one_or_none()
        )

    @staticmethod
    def add(user_id: int, name: str, avatar):
        if User.get(user_id) is not None:
            return

        user = User(user_id=user_id, name=name, avatar=avatar)
        session.add(user)
        session.commit()

    def __repr__(self):
        return f'<User user_id="{self.user_id}" name="{self.name}">'


class Message(database.base):
    __tablename__ = "messages"

    message_id = Column(BigInteger, primary_key=True)
    author_id = Column(BigInteger)
    text = Column(String)
    attachments = Column(String, default=None)
    embeds = Column(String, default=None)

    @staticmethod
    def get(message_id: int):
        return (
            session.query(Message)
            .filter(
                Message.message_id == message_id,
            )
            .one_or_none()
        )

    @staticmethod
    def add(
        message_id: int,
        author_id: int,
        text: str,
        *,
        attachments: str = None,
        embeds: list = None,
    ):
        if Message.get(message_id) is not None:
            return

        message = Message(
            message_id=message_id,
            author_id=author_id,
            text=text,
            attachments=attachments,
            embeds=embeds,
        )
        session.add(message)
        session.commit()

    def __repr__(self):
        return (
            f'<Message message_id="{self.message_id}" author_id="{self.author_id}" '
            f'text="{self.text}" attachments="{self.attachments}" embeds="{self.embeds}">'
        )


wipe()
init()
