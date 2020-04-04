from config import config, messages


class BaseRepository:

    def __init__(self):
        self.config = config.config
        self.messages = messages.Messages
