from .warden import Warden


def setup(bot):
    """Load cog"""
    bot.add_cog(Warden(bot))
