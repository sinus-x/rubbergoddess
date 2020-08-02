from .karma import Karma


def setup(bot):
    """Load cog"""
    bot.add_cog(Karma(bot))
