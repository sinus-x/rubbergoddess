from discord.ext import commands
from config.config import Config as config
from features import verification
from repository import user_repo
import utils

user_r = user_repo.UserRepository()

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification = verification.Verification(bot, user_r)

    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.user)
    @commands.command()
    async def submit(self, ctx):
        await self.verification.verify(ctx.message)

    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.user)
    @commands.command(aliases=["getcode"])
    async def verify(self, ctx):
        await self.verification.send_code(ctx.message)

    @submit.error
    @verify.error
    async def verify_checks_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(utils.fill_message( "verify_wrong_channel", user=ctx.author.id))

def setup(bot):
    bot.add_cog(Verify(bot))
