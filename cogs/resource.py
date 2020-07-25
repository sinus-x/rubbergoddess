import re
from collections import OrderedDict

import hjson
import discord

from core.emote import emote


class CogConfig:
    """Configuration manager"""

    def __init__(self, cog_name: str):
        # load default configuration
        self.config = hjson.load(open(f"cogs/{cog_name}/config.default.hjson"))

        # load custom configuration
        try:
            custom = hjson.load(open(f"cogs/{cog_name}/config.hjson"))

            for key, value in self.config.items():
                # allow two layers
                if isinstance(value, OrderedDict) or isinstance(value, dict):
                    for subkey in value.keys():
                        if subkey in custom[key]:
                            self.config[key][subkey] = custom[key][subkey]
                elif key in custom.keys():
                    self.config[key] = custom[key]
        except:
            # there is no custom config
            pass

    def get(self, *args):
        result = self.config
        for arg in args:
            if arg in result:
                result = result[arg]
            else:
                raise ValueError(f"`{'/'.join(args)}` is not valid config argument.")
        return result


class CogText:
    """Text manager"""

    def __init__(self, cog_name: str):
        # load default strings
        self.config = hjson.load(open(f"cogs/{cog_name}/text.default.hjson"))

        # load custom strings
        try:
            custom = hjson.load(open(f"cogs/{cog_name}/text.hjson"))

            for key, value in self.config.items():
                # allow two layers
                if isinstance(value, OrderedDict) or isinstance(value, dict):
                    for subkey in value.keys():
                        if subkey in custom[key]:
                            self.config[key][subkey] = custom[key][subkey]
                elif key in custom.keys():
                    self.config[key] = custom[key]
        except:
            # there is no custom config
            pass

    def get(self, *args, **kwargs):
        # get string
        result = self.config
        for arg in args:
            if arg in result:
                result = result[arg]
            else:
                raise ValueError(f"`{'/'.join(args)}` is not valid text file argument.")

        # apply emojis
        emojis = re.findall(r"\(\(emoji\.([a-z]+)\)\)", result)
        for emoji in emojis:
            result = result.replace(f"((emoji.{emoji}))", emote.get(emoji))

        # apply kwargs
        for key, value in kwargs.items():
            string = "((" + key + "))"
            if string in result:
                result = result.replace(string, str(value))
            else:
                raise ValueError(f"Requested string `{'/'.join(args)}` does not have key `{key}`.")

        return result
