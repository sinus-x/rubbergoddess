from .acl import ACL


def setup(bot):
    bot.add_cog(ACL(bot))
