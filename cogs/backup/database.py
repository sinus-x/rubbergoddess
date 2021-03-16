from sqlalchemy import create_engine, Column, String, BigInteger, LargeBinary
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
    init()


class Information(database.base):
    __tablename__ = "information"

    id = Column(BigInteger, primary_key=True)
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
            id=guild_id,
            channel_id=channel_id,
            author_id=author_id,
        )
        session.add(information)
        session.commit()

    def __repr__(self):
        return (
            f'<Information id="{self.id}" '
            f'channel_id="{self.channel_id}" author_id="{self.author_id}">'
        )


class User(database.base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    avatar = Column(LargeBinary)

    @staticmethod
    def get(user_id: int):
        return session.query(User).filter(User.id == user_id).one_or_none()

    @staticmethod
    def add(user_id: int, name: str, avatar):
        if User.get(user_id) is not None:
            return

        user = User(id=user_id, name=name, avatar=avatar)
        session.add(user)
        session.commit()

    def __repr__(self):
        return f'<User id="{self.id}" name="{self.name}">'


class Emoji(database.base):
    __tablename__ = "emojis"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    data = Column(LargeBinary)

    @staticmethod
    def get(emoji_id: int):
        return session.query(Emoji).filter(Emoji.id == emoji_id).one_or_none()

    @staticmethod
    def add(emoji_id: int, name: str, data):
        if Emoji.get(emoji_id) is not None:
            return

        emoji = Emoji(id=emoji_id, name=name, data=data)
        session.add(emoji)
        session.commit()

    def __repr__(self):
        return f'<Emoji id="{self.id}" name="{self.name}">'


class Message(database.base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    author_id = Column(BigInteger)
    text = Column(String)
    attachments = Column(String, default=None)
    embeds = Column(String, default=None)

    @staticmethod
    def get(message_id: int):
        return session.query(Message).filter(Message.id == message_id).one_or_none()

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
            id=message_id,
            author_id=author_id,
            text=text,
            attachments=attachments,
            embeds=embeds,
        )
        session.add(message)
        session.commit()

    def __repr__(self):
        return (
            f'<Message id="{self.id}" author_id="{self.author_id}" '
            f'text="{self.text}" attachments="{self.attachments}" embeds="{self.embeds}">'
        )


wipe()
