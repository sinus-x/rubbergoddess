# Rubbergoddess

**This document needs updating before it is declared as master!**

![Rubbergoddess](https://repository-images.githubusercontent.com/238499660/ec829180-4868-11ea-948c-199e65da1347)

## About

This FEKTwide Discord bot manages the verification process, karma and some other
commands on VUT FEKT Discord server. [Rubbergod](https://github.com/Toaster192/rubbergod)'s younger sister.

## Installing and running the bot

See [wiki](https://github.com/sinus-x/rubbergoddess/wiki).

### Using the bot
Please note that the current state is not ready to be used on multiple servers. 

For example:
```python
    @commands.guild_only()
    @commands.group(aliases=["db"])
    @commands.has_any_role('MOD', 'SUBMOD')
    async def database (self, ctx: commands.Context):
```

This may seem safe. And it is, if the bot is on your guild only. If the bot is 
set as public or you have put it somewhere else, the other guild's owner/mods 
can read your database on their server.

## Authors

Rubbergoddess is mantained by [sinus-x](https://github.com/sinus-x) and 
[Czechbol](https://github.com/Czechbol).

Original authors include [Toaster](https://github.com/toaster192), 
[Matthew](https://github.com/matejsoroka), [Fpmk](https://github.com/TheGreatfpmK), 
[peter](https://github.com/peterdragun), [Urumasi](https://github.com/Urumasi) 
or [Leo](https://github.com/ondryaso).

## License

This project is licensed under the GNU GPL v.3 License.

Rubbergoddess image is a CC0 photography by Peter Sjo hosted on 
[unsplash.com](https://unsplash.com/photos/Nxy-6QwGMzA).
