import json
import re

import discord

from core.config import config
from core.emote import emote


class Text:
    """Manage string values"""

    def __init__(self):
        self.default = json.load(open("config/text.default.json", "r"))
        try:
            self.custom = json.load(open("config/text.json", "r"))
        except FileNotFoundError:
            self.custom = None

    def get(self, group: str, key: str):
        if self.custom is not None and group in self.custom and key in self.custom.get(group):
            result = self.custom.get(group).get(key)
        elif group in self.default and key in self.default.get(group):
            result = self.default.get(group).get(key)
        else:
            return None

        if isinstance(result, list):
            return [self._replace(x) for x in result]
        if isinstance(result, str):
            return self._replace(result)
        return result

    def fill(self, group: str, key: str, **kwargs):
        result = self.get(group, key)

        if "nickname" in kwargs:
            kwargs["nickname"] = self._escape_user(kwargs["nickname"])
        if "user" in kwargs:
            kwargs["user"] = self._mention_user(kwargs["user"])
        if "admin" in kwargs:
            kwargs["admin"] = self._mention_user(config.admin_id)
        if "role" in kwargs:
            kwargs["role"] = self._mention_role(kwargs["role"])
        if "channel" in kwargs:
            kwargs["channel"] = self._mention_channel(kwargs["channel"])

        for key in kwargs:
            if "{" + key + "}" in result:
                result = result.replace("{" + key + "}", str(kwargs[key]))
        return result

    def _replace(self, string: str):
        # substitute emotes
        emotes = re.findall(r"{emote\.([a-z]+)}", string)
        for e in emotes:
            string = string.replace("{emote." + e + "}", emote.get(e))

        # substitute prefix
        string = string.replace("{prefix}", config.prefix)

        return string

    def _escape_user(self, user):
        if isinstance(user, discord.Member):
            user = user.display_name
        return discord.utils.escape_markdown(str(user))

    def _mention_user(self, user):
        if isinstance(user, discord.Member) or isinstance(user, discord.User):
            return user.mention
        if isinstance(user, int):
            return f"<@!{user}>"
        return str(user)

    def _mention_channel(self, channel):
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
            return channel.mention
        if isinstance(channel, int):
            return f"<#{channel}>"
        return str(channel)

    def _mention_role(self, role):
        if isinstance(role, discord.Role):
            return role.mention
        if isinstance(role, int):
            return f"<@&{role}>"
        return str(role)


text = Text()
