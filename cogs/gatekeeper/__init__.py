from .gatekeeper import Gatekeeper


def setup(bot):
    """Load cog"""
    bot.add_cog(Gatekeeper(bot))
