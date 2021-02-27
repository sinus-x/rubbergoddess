# Contributing

**NOTE**: We're planning to migrate the codebase to the [pumpkin.py](https://github.com/Pumpkin-py) project. All the functions from this bot will be moved there.

## Repository setup

- Fork the repository
- Clone your fork: `git clone git@github.com/<your-nickname>/rubbergoddess.git`
- `cd rubbergoddess`
- Add upstream: `git remote add upstream git@github.com:sinus-x/rubbergoddess.git`
- Create your feature branch: `git checkout master && git branch my-feature && git checkout my-feature`
- Open your pull requests from this branch

## Bot setup

```bash
# Download, create and enable venv environment
sudo apt install python3-venv
python3 -m pip install venv
python3 -m venv .venv
source .venv/bin/activate

# Install bot packages
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt

# Enable pre-commit
pre-commit install
```

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
```
