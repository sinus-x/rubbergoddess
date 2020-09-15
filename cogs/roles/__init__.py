from .roles import Roles


def setup(bot):
    """Load cog"""
    bot.add_cog(Roles(bot))
