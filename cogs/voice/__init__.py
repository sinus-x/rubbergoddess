from .voice import Voice


def setup(bot):
    """Load cog"""
    bot.add_cog(Voice(bot))
