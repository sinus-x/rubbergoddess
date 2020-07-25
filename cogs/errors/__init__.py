from .errors import Errors


def setup(bot):
    """Load cog"""
    bot.add_cog(Errors(bot))
