from .howto import Howto


def setup(bot):
    """Load cog"""
    bot.add_cog(Howto(bot))
