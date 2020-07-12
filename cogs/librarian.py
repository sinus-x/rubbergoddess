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
    async def weather(self, ctx, *, city: str = "Brno"):
        token = config.get("librarian", "weather token")
        city = city[:100]
        url = (
            "http://api.openweathermap.org/data/2.5/weather?q="
            + city
            + "&units=metric&lang=cz&appid="
            + token
        )
        res = requests.get(url).json()

        if str(res["cod"]) == "200":
            description = "Aktuální počasí v městě " + res["name"] + ", " + res["sys"]["country"]
            embed = discord.Embed(title="Počasí", description=description)
            image = "http://openweathermap.org/img/w/" + res["weather"][0]["icon"] + ".png"
            embed.set_thumbnail(url=image)
            weather = res["weather"][0]["main"] + " (" + res["weather"][0]["description"] + ")"
            temp = str(res["main"]["temp"]) + "°C"
            feels_temp = str(res["main"]["feels_like"]) + "°C"
            humidity = str(res["main"]["humidity"]) + "%"
            wind = str(res["wind"]["speed"]) + "m/s"
            clouds = str(res["clouds"]["all"]) + "%"
            visibility = str(res["visibility"] / 1000) + " km" if "visibility" in res else "bez dat"
            embed.add_field(name="Počasí", value=weather, inline=False)
            embed.add_field(name="Teplota", value=temp, inline=True)
            embed.add_field(name="Pocitová teplota", value=feels_temp, inline=True)
            embed.add_field(name="Vlhkost", value=humidity, inline=True)
            embed.add_field(name="Vítr", value=wind, inline=True)
            embed.add_field(name="Oblačnost", value=clouds, inline=True)
            embed.add_field(name="Viditelnost", value=visibility, inline=True)
            await ctx.send(embed=embed)
        elif str(res["cod"]) == "404":
            await ctx.send("Město nenalezeno")
        elif str(res["cod"]) == "401":
            await ctx.send("Rip token")
        else:
            await ctx.send("Město nenalezeno! " + emote.sad + " (" + res["message"] + ")")

        await utils.delete(ctx)
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
