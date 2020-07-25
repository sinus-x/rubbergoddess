from .admin import Admin


def setup(bot):
    """Load cog"""
    bot.add_cog(Admin(bot))
