from .janitor import Janitor


def setup(bot):
    """Load cog"""
    bot.add_cog(Janitor(bot))
