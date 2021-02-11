import base64
import hashlib
from datetime import date

from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import rubbercog, utils


class Librarian(rubbercog.Rubbercog):
    """Knowledge and information based commands"""

    # TODO Move czech strings to text.default.json

    def __init__(self, bot):
        super().__init__(bot)

        self.config = CogConfig("librarian")
        self.text = CogText("librarian")

    @commands.command(aliases=["svátek"])
    async def svatek(self, ctx):
        url = f"http://svatky.adresa.info/json?date={date.today().strftime('%d%m')}"
        res = await utils.fetch_json(url)
        names = []
        for i in res:
            names.append(i["name"])
        if len(names):
            await ctx.send(self.text.get("nameday", "cs", name=", ".join(names)))
        else:
            await ctx.send(self.text.get("nameday", "cs0"))

    @commands.command(aliases=["sviatok"])
    async def meniny(self, ctx):
        url = f"http://svatky.adresa.info/json?lang=sk&date={date.today().strftime('%d%m')}"
        res = await utils.fetch_json(url)
        names = []
        for i in res:
            names.append(i["name"])
        if len(names):
            await ctx.send(self.text.get("nameday", "sk", name=", ".join(names)))
        else:
            await ctx.send(self.text.get("nameday", "sk0"))

    @commands.command(aliases=["tyden", "týden", "tyzden", "týždeň"])
    async def week(self, ctx: commands.Context):
        """See if the current week is odd or even"""
        cal_week = date.today().isocalendar()[1]
        stud_week = cal_week - self.config.get("starting_week") + 1
        even, odd = self.text.get("week", "even"), self.text.get("week", "odd")
        cal_type = even if cal_week % 2 == 0 else odd
        stud_type = even if stud_week % 2 == 0 else odd

        embed = self.embed(ctx=ctx)
        embed.add_field(
            name=self.text.get("week", "study"),
            value="{} ({})".format(stud_type, stud_week),
        )
        embed.add_field(
            name=self.text.get("week", "calendar"),
            value="{} ({})".format(cal_type, cal_week),
        )
        await ctx.send(embed=embed)

        await utils.delete(ctx)
        await utils.room_check(ctx)

    @commands.command(aliases=["počasí", "pocasi", "počasie", "pocasie"])
    async def weather(self, ctx, *, place: str = "Brno"):
        token = self.config.get("weather_token")
        place = place[:100]

        if "&" in place:
            return await ctx.send(self.text.get("weather", "place_not_found"))

        url = (
            "https://api.openweathermap.org/data/2.5/weather?q="
            + place
            + "&units=metric&lang=cz&appid="
            + token
        )
        res = await utils.fetch_json(url)

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
            return await ctx.send(self.text.get("weather", "place_not_found"))
        elif str(res["cod"]) == "401":
            return await ctx.send(self.text.get("weather", "token"))
        elif str(res["cod"]) != "200":
            return await ctx.send(self.text.get("weather", "place_error", message=res["message"]))

        title = res["weather"][0]["description"]
        description = (
            self.text.get("weather", "description", name=res["name"], country=res["sys"]["country"])
            if "country" in res["sys"]
            else self.text.get("weather", "description_short", name=res["name"])
        )
        if description.endswith("CZ"):
            description = description[:-4]
        embed = self.embed(ctx=ctx, title=title[0].upper() + title[1:], description=description)
        embed.set_thumbnail(
            url="https://openweathermap.org/img/w/{}.png".format(res["weather"][0]["icon"])
        )

        embed.add_field(
            name=self.text.get("weather", "temperature"),
            value=self.text.get(
                "weather",
                "temperature_value",
                real=round(res["main"]["temp"], 1),
                feel=round(res["main"]["feels_like"], 1),
            )
            + "\n"
            + self.text.get(
                "weather",
                "temperature_minmax",
                min=round(res["main"]["temp_min"], 1),
                max=round(res["main"]["temp_max"], 1),
            ),
            inline=False,
        )

        embed.add_field(
            name=self.text.get("weather", "humidity"),
            value=str(res["main"]["humidity"]) + " %",
        )
        embed.add_field(
            name=self.text.get("weather", "clouds"),
            value=(str(res["clouds"]["all"]) + " %"),
        )
        if "visibility" in res:
            if res["visibility"] == 10000:
                value = self.text.get("weather", "visibility_max")
            else:
                value = f"{res['visibility']/1000} km"
            embed.add_field(
                name=self.text.get("weather", "visibility"),
                value=value,
            )
        embed.add_field(name=self.text.get("weather", "wind"), value=f"{res['wind']['speed']} m/s")

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
        result = "**hashlib**\n"
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
            return await ctx.send(self.text.get("invalid_hash"))

        quote = self.sanitise(data[:50]) + ("…" if len(data) > 50 else "")
        await ctx.send(f"**{fn}** ({quote}):\n> ```{result}```")

    @commands.command(aliases=["maclookup"])
    async def macaddress(self, ctx, mac: str):
        """Get information about MAC address"""
        apikey = self.config.get("maclookup_token")

        if apikey == 0:
            return await self.output.error(
                ctx,
                self.text.get("maclookup", "no_token"),
            )

        if "&" in mac or "?" in mac:
            return await self.output.error(
                ctx,
                self.text.get("maclookup", "bad_mac", mention=ctx.author.mention),
            )

        url = f"https://api.maclookup.app/v2/macs/{mac}?format=json&apiKey={apikey}"
        res = await utils.fetch_json(url)

        if res["success"] is False:
            embed = self.embed(
                ctx=ctx,
                title=self.text.get("maclookup", "error", errcode=res["errorCode"]),
                description=res["error"],
                footer="maclookup.app",
            )
            return await ctx.send(embed=embed)

        if res["found"] is False:
            embed = self.embed(
                ctx=ctx,
                title=self.text.get("maclookup", "error", errcode="404"),
                description=self.text.get("maclookup", "not_found"),
                footer="maclookup.app",
            )
            return await ctx.send(embed=embed)

        embed = self.embed(ctx=ctx, title=res["macPrefix"], footer="maclookup.app")
        embed.add_field(
            name=self.text.get("maclookup", "company"),
            value=res["company"],
            inline=False,
        )
        embed.add_field(name=self.text.get("maclookup", "country"), value=res["country"])

        block = f"`{res['blockStart']}`"
        if res["blockStart"] != res["blockEnd"]:
            block += f"\n`{res['blockEnd']}`"
        embed.add_field(name=self.text.get("maclookup", "block"), value=f'`{res["blockStart"]}`')

        await ctx.send(embed=embed)

    @commands.cooldown(rate=2, per=20, type=commands.BucketType.user)
    # The API has limit of 45 requests per minute
    @commands.cooldown(rate=45, per=55, type=commands.BucketType.default)
    @commands.command(aliases=["iplookup"])
    async def ipaddress(self, ctx, query: str):
        """Get information about an IP address or a domain name"""
        if "&" in query or "?" in query or not len(query):
            return await self.output.error(
                ctx,
                self.text.get("iplookup", "bad_query", mention=ctx.author.mention),
            )

        url = (
            f"http://ip-api.com/json/{query}"
            "?fields=query,status,message,country,regionName,city,lat,lon,isp,org"
        )
        res = await utils.fetch_json(url)
        # TODO The API states that we should be listening for the `X-Rl` header.
        # If it is `0`, we must stop for `X-ttl` seconds.
        # https://ip-api.com/docs/api:json

        if res["status"] == "fail":
            embed = self.embed(
                ctx=ctx,
                title=self.text.get("iplookup", "error"),
                description="`" + res["message"] + "`",
                footer="ip-api.com",
            )
            return await ctx.send(embed=embed)

        embed = self.embed(ctx=ctx, title=res["query"], footer="ip-api.com")
        embed.add_field(
            name=res["city"],
            value=f"{res['regionName']}, {res['country']}",
            inline=False,
        )
        embed.add_field(
            name=self.text.get("iplookup", "geo"),
            value=f"{res['lon']}, {res['lat']}",
        )
        embed.add_field(
            name=self.text.get("iplookup", "org"),
            value=res["org"],
        )
        embed.add_field(
            name=self.text.get("iplookup", "isp"),
            value=res["isp"],
        )

        await ctx.send(embed=embed)
