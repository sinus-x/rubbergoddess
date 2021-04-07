import asyncio
import time
from io import BytesIO

import discord
from discord.ext import commands
import dhash
from PIL import Image

from cogs.resource import CogConfig, CogText
from core import acl, rubbercog, utils
from core.config import config
from core.emote import emote
from repository import image_repo, karma_repo

dhash.force_pil()
repo_i = image_repo.ImageRepository()
repo_k = karma_repo.KarmaRepository()


class Warden(rubbercog.Rubbercog):
    """A cog for database lookups"""

    # TODO Implement template matching to prevent false positives

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("warden")
        self.text = CogText("warden")

        self.limit_full = 3
        self.limit_hard = 7
        self.limit_soft = 14


def setup(bot):
    bot.add_cog(Warden(bot))
