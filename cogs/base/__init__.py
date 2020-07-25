from .base import Base


def setup(bot):
    """Load cog"""
    bot.add_cog(Base(bot))
