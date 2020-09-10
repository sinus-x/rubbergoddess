from .semester import Semester


def setup(bot):
    """Load cog"""
    bot.add_cog(Semester(bot))
