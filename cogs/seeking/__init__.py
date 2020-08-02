from .seeking import Seeking


def setup(bot):
    """Load cog"""
    bot.add_cog(Seeking(bot))
