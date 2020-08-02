from .animals import Animals


def setup(bot):
    """Load cog"""
    bot.add_cog(Animals(bot))
