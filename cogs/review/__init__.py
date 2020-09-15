from .review import Review


def setup(bot):
    """Load cog"""
    bot.add_cog(Review(bot))
