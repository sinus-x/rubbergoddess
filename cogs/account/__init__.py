from .account import Account


def setup(bot):
    """Load cog"""
    bot.add_cog(Account(bot))
