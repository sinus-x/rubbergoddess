from .meme import Meme


def setup(bot):
    """Load cog"""
    bot.add_cog(Meme(bot))
