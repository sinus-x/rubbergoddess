from .sync import Sync


def setup(bot):
    """Load cog"""
    bot.add_cog(Sync(bot))
