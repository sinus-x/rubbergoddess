from .librarian import Librarian


def setup(bot):
    """Load cog"""
    bot.add_cog(Librarian(bot))
