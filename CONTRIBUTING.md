# Contributing

## How to write an cog?

Use the Rubbercog class:

```python
from core import rubbercog

class MyCog(rubbercog.Rubbercog):
    """Short cog description"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

        # If the cog implements functionality that anyone can use,
        # set visibility to True. Use False otherwise.
        self.visible = True
```

Use command groups to organise nested commands:

```python
@commands.group(name="foo")
async def foo(self, ctx: commands.Context):
	"""Do stuff"""
	if ctx.invoked_subcommand is None:
		await self.throwHelp(ctx)

@foo.group(name="bar")
async def foo_bar(self, ctx: commands.Context):
	"""Do cool stuff"""
	if ctx.invoked_subcommand is None:
		await self.throwHelp(ctx)

@foo_bar.command(name="baz")
async def foo_bar_baz(self, ctx: commands.Context):
	"""Do crazy stuff"""
	ctx.send("Foo.")
```

---

The Rubbercog implements some functions to help you with Discord objects: 
`getGuild()`, `getModRole()`, `getVerifyRole()`, `getElevatedRoles()`.

It also includes a helper function `_getEmbed(ctx)`, which initiates Embed for 
output.

---

To show an error/notification/help to the user, call one of the throw functions:

```python
await self.throwError(ctx, messages.exc_not_implemented)
return
# or
await self.throwNotification(ctx, "Wrong channel.")
return
# or
await self.throwHelp(ctx)
return
```

**Note**: Help embeds are generated from docstrings in the code.

To log error or information use the `log(ctx, msg)` function:

```python
try:
	# some code
	# Log that user performed an action
	await self.log(ctx, "?function", quote=False)
except Exception as e:
	# Log that an error occured
	await self.throwError(ctx, e)
	await self.log(ctx, "cog:function_name", error=e, quote=True)
	return
```

These messages will be sent to the guild log channel.

---

Usually, when the bot sends an embed, it deletes the original message:

```python
await self.deleteCommand(ctx)
```

