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

## Development

Please refer to the [wiki](https://github.com/sinus-x/rubbergoddess/wiki/4.0-developers).

In short: We do have a
[Rubbercog](https://github.com/sinus-x/rubbergoddess/blob/master/core/rubbercog.py)
class that manages some of the common tasks, two logging classes in
[output.py](https://github.com/sinus-x/rubbergoddess/blob/master/core/output.py)
(Output and Console).

Configuration is loaded via imported
[config](https://github.com/sinus-x/rubbergoddess/blob/master/core/config.py)
object, strings reside inside of
[text](https://github.com/sinus-x/rubbergoddess/blob/master/core/config.py) --
each cog has its dictionary in respective hjson file.
