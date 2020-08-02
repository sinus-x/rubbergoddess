from .actress import Actress


def setup(bot):
    """Load cog"""
    bot.add_cog(Actress(bot))
