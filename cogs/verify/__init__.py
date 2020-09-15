from .verify import Verify


def setup(bot):
    """Load cog"""
    bot.add_cog(Verify(bot))
