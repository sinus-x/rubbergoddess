from .judge import Judge


def setup(bot):
    """Load cog"""
    bot.add_cog(Judge(bot))
