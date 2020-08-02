from .faceshifter import Faceshifter


def setup(bot):
    """Load cog"""
    bot.add_cog(Faceshifter(bot))
