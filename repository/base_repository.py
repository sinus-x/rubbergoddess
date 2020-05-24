from core.config import config
from config.messages import Messages


class BaseRepository:
    def __init__(self):
        self.config = config
        self.messages = Messages
