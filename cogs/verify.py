from discord.ext import commands
from config.config import Config as config
from config.messages import Messages as messages
from cogs import errors
from features import verification
from repository import user_repo
import utils

repository = user_repo.UserRepository()

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.errors = errors.Errors(bot)
        self.verification = verification.Verification(bot, repository)

    async def in_jail (ctx):
        """Return true if current channel is #jail"""
        if ctx.guild is None:
            # allow verification in DMs
            return True
        return ctx.channel.id == config.channel_jail

    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.user)
    @commands.check(in_jail)
    @commands.command()
    async def submit(self, ctx):
        await self.verification.verify(ctx.message)

    @commands.cooldown(rate=5, per=30.0, type=commands.BucketType.user)
    @commands.check(in_jail)
    @commands.command(aliases=["getcode"])
    async def verify(self, ctx):
        await self.verification.send_code(ctx.message)

    @submit.error
    @verify.error
    async def verifyError (self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.errors._getNotification(ctx, messages.verify_not_jail)
            return

def setup(bot):
    bot.add_cog(Verify(bot))
