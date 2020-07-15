← Back to [module list](index.md) or [home](../index.md)

# Howto

## User commands

### howto (path)

Get information about... stuff.

## Privileged commands

This module has no commands only usable by privileged users.

## Resources

Data are taken from local file: `data/howto/howto.hjson`.

Example configuration:

```hjson
{
	category: {
		subcategory:
			"""
			- First, do this
			- Then do that
			- Finish with that
			"""

		another:
			"""
			- Try something
			- Try something else
			"""
	}

	2nd: {
		item: [
			step 1 description
			step 2 description
			step 3 description
		]
	}
}
```


← Back to [module list](index.md) or [home](../index.md)
