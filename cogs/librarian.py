import base64
import requests
import hashlib
from datetime import date

import discord
from discord.ext import commands

from core import rubbercog, utils
from core.config import config
from core.text import text
from core.emote import emote


class Librarian(rubbercog.Rubbercog):
    """Knowledge and information based commands"""

    # TODO Move czech strings to text.default.json

    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(aliases=["svátek"])
    async def svatek(self, ctx):
        url = f"http://svatky.adresa.info/json?date={date.today().strftime('%d%m')}"
        res = requests.get(url).json()
        names = []
        for i in res:
            names.append(i["name"])
        await ctx.send(text.fill("librarian", "nameday cz", name=", ".join(names)))

    @commands.command(aliases=["sviatok"])
    async def meniny(self, ctx):
        url = f"http://svatky.adresa.info/json?lang=sk&date={date.today().strftime('%d%m')}"
        res = requests.get(url).json()
        names = []
        for i in res:
            names.append(i["name"])
        await ctx.send(text.fill("librarian", "nameday sk", name=", ".join(names)))

    @commands.command(aliases=["tyden", "týden", "tyzden", "týždeň"])
    async def week(self, ctx: commands.Context):
        """See if the current week is odd or even"""
        starting_week = config.get("librarian", "starting week")
        cal_week = date.today().isocalendar()[1]
        stud_week = cal_week - starting_week
        even, odd = "sudý", "lichý"
        cal_type = even if cal_week % 2 == 0 else odd
        stud_type = even if stud_week % 2 == 0 else odd

        embed = self.embed(ctx=ctx)
        embed.add_field(name="Studijní", value="{} ({})".format(stud_type, stud_week))
        embed.add_field(name="Kalendářní", value="{} ({})".format(cal_type, cal_week))
        await ctx.send(embed=embed)

        await utils.delete(ctx)

    @commands.command(aliases=["počasí", "pocasi", "počasie", "pocasie"])
    async def weather(self, ctx, *, place: str = "Brno"):
        token = config.get("librarian", "weather token")
        place = place[:100]
        url = (
            "https://api.openweathermap.org/data/2.5/weather?q="
            + place
            + "&units=metric&lang=cz&appid="
            + token
        )
        res = requests.get(url).json()

        """ Example response
        {
            "coord":{
                "lon":16.61,
                "lat":49.2
            },
            "weather":[
                {
                    "id":800,
                    "temp_maixn":"Clear",
                    "description":"jasno",
                    "icon":"01d"
                }
            ],
            "base":"stations",
            "main":{
                "temp":21.98,
                "feels_like":19.72,
                "temp_min":20.56,
                "temp_max":23,
                "pressure":1013,
                "humidity":53
            },
            "visibility":10000,
            "wind":{
                "speed":4.1,
                "deg":50
            },
            "clouds":{
                "all":0
            },
            "dt":1595529518,
            "sys":{
                "type":1,
                "id":6851,
                "country":"CZ",
                "sunrise":1595474051,
                "sunset":1595529934
            },
            "timezone":7200,
            "id":3078610,
            "name":"Brno",
            "cod":200
        }
        """

        if str(res["cod"]) == "404":
            return await ctx.send(text.get("librarian", "place not found"))
        elif str(res["cod"]) == "401":
            return await ctx.send(text.get("librarian", "weather token"))
        elif str(res["cod"]) != "200":
            return await ctx.send(text.fill("librarian", "place error", message=res["message"]))

        title = res["weather"][0]["description"]
        description = text.fill(
            "librarian", "w_description", name=res["name"], country=res["sys"]["country"]
        )
        if description.endswith("CZ"):
            description = description[:-4]
        embed = self.embed(ctx=ctx, title=title[0].upper() + title[1:], description=description)
        embed.set_thumbnail(
            url="https://openweathermap.org/img/w/{}.png".format(res["weather"][0]["icon"])
        )

        embed.add_field(
            name=text.get("librarian", "w_temperature"),
            value=text.fill(
                "librarian",
                "w_temperature_value",
                real=round(res["main"]["temp"], 1),
                feel=round(res["main"]["feels_like"], 1),
            ),
            inline=False,
        )

        embed.add_field(
            name=text.get("librarian", "w_humidity"), value=str(res["main"]["humidity"]) + " %",
        )
        embed.add_field(
            name=text.get("librarian", "w_clouds"), value=(str(res["clouds"]["all"]) + " %")
        )
        if "visibility" in res:
            embed.add_field(
                name=text.get("librarian", "w_visibility"),
                value=f"{int(res['visibility']/1000)} km",
            )
        embed.add_field(name=text.get("librarian", "w_wind"), value=f"{res['wind']['speed']} m/s")

        await utils.send(ctx, embed=embed)
        await utils.room_check(ctx)

    @commands.command(aliases=["b64"])
    async def base64(self, ctx, direction: str, *, data: str):
        """Get base64 data

        direction: [encode, e, -e; decode, d, -d]
        text: string (under 1000 characters)
        """
        if data is None or not len(data):
            return await utils.send_help(ctx)

        data = data[:1000]
        if direction in ("encode", "e", "-e"):
            direction = "encode"
            result = base64.b64encode(data.encode("utf-8")).decode("utf-8")
        elif direction in ("decode", "d", "-d"):
            direction = "decode"
            try:
                result = base64.b64decode(data.encode("utf-8")).decode("utf-8")
            except Exception as e:
                return await ctx.send(f"> {e}")
        else:
            return await utils.send_help(ctx)

        quote = self.sanitise(data[:50]) + ("…" if len(data) > 50 else "")
        await ctx.send(f"**base64 {direction}** ({quote}):\n> ```{result}```")

        await utils.room_check(ctx)

    @commands.command()
    async def hashlist(self, ctx):
        """Get list of available hash functions"""
        result = f"**hashlib**\n"
        result += "> " + " ".join(sorted(hashlib.algorithms_available))

        await ctx.send(result)

    @commands.command()
    async def hash(self, ctx, fn: str, *, data: str):
        """Get hash function result

        Run hashlist command to see available algorithms
        """
        if fn in hashlib.algorithms_available:
            result = hashlib.new(fn, data.encode("utf-8")).hexdigest()
        else:
            return await ctx.send(text.get("librarian", "hash not found"))

        quote = self.sanitise(data[:50]) + ("…" if len(data) > 50 else "")
        await ctx.send(f"**{fn}** ({quote}):\n> ```{result}```")


def setup(bot):
    bot.add_cog(Librarian(bot))
