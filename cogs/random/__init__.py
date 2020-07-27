from .random import Random


def setup(bot):
    """Load cog"""
    bot.add_cog(Random(bot))
