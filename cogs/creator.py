import discord
from discord.ext import commands

from core import rubbercog
from config.config import config

class Creator(rubbercog.Rubbercog):
    """Initiate the server for the next semester"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

"""
?init
- group

?init reset
- delete all channels
- switch FEKT/VUT roles to REVERIFY
  ^^ WE NEED TO DISCUSS THE MECHANICS, IT IS HIGHLY CONNECTED TO THE VERIFY

?init channels
- load departments
 - add subjects with their names as descriptions
   - Should subjects with different shortcuts but same names be merged?

?init subjects
- department header (image, pinned)
- react-to-role subjects

"""

def setup(bot):
    bot.add_cog(Creator(bot))
