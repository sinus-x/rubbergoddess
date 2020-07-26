from .stalker import Stalker


def setup(bot):
    """Load cog"""
    bot.add_cog(Stalker(bot))
