# Contributing

## Tell us first

When contributing to this repository, first discuss the change you wish to make
via issue, on Discord or any other way.

## Pull Request process

Make sure no trailing `print()`s are present in the code, use flake8 and black
with configuration present in this repository.

Your PR must not break current configuration or database scheme, unless you
have serious reason to do so.

Always open pull requests against the `devel` branch. Your PR must pass the
build in Github Actions.

## Cog organisation

Each module has its directory in `cogs/`, inside of it there is `__init__.py` file and file with the same name as its directory:

```py
from .test import Test

def setup(bot):
	"""Load test cog"""
	bot.add_cog(Test(bot))
```

The module itself is usually single class. Please follow this import ordering:

```py
# general
import base64
import random

# discord.py
import discord
from discord.ext import commands

# bot
from cogs.resource import CogConfig, CotText
from core import rubbercog, utils
```

The class has four parts: init, commands, logic, helper functions and error catching. Not all parts have to be present.

```py
class Test(rubbercog.Rubbercog):
	"""Test cog"""

	def __init__(self, bot):
		super().__init__(bot)

		self.config = CogConfig("test")
		self.text = CogText("test")

		# additional setup

	##
	## Commands
	##

	@commands.group(name="foo")
	async def foo(self, ctx):
		"""Command group"""
		await utils.send_help(ctx)

	@foo.command()
	async def foo_bar(self, ctx):
		"""Do bar"""
		await ctx.send("Functinality.")

	##
	## Logic
	##

	def fill_embed(self, ctx: commands.Context) -> discord.Embed:
		pass

	##
	## Helper functions
	##

	def send_if_guild(self, ctx: commands.Context):
		pass

	##
	## Error catching
	##

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if hasattr(ctx.command, "on_error") or hasattr(ctx.command, "on_command_error"):
			return
		error = getattr(error, "original", error)

		if not isintance(error, TestError):
			return

		await ctx.send("Custom text module error :(")

class TestError(rubbercog.RubbercogException):
	pass
```
