from discord.ext import commands
from config.config import Config as config
from features import verification
from repository import user_repo

user_r = user_repo.UserRepository()

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification = verification.Verification(bot, user_r)

    async def is_in_jail(ctx):
        return ctx.message.channel.id == config.jail

    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.user)
    @commands.check(is_in_jail)
    @commands.command()
    async def submit(self, ctx):
        await self.verification.verify(ctx.message)

    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.user)
    @commands.check(is_in_jail)
    @commands.command(aliases=["getcode"])
    async def verify(self, ctx):
        await self.verification.send_code(ctx.message)


def setup(bot):
    bot.add_cog(Verify(bot))
