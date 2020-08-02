from .shop import Shop


def setup(bot):
    """Load cog"""
    bot.add_cog(Shop(bot))
