import json
import requests

import discord
from discord.ext import commands

from core import rubbercog, utils
from config.config import config
from config.messages import Messages as messages

class Librarian(rubbercog.Rubbercog):
    """Set of knowledge- and informatin based commands"""
    def __init__(self, bot):
        self.bot = bot
        self.visible = True

    @commands.command(aliases=["svátek"])
    async def svatek(self, ctx):
        url = config.nameday_cz
        res = requests.get(url).json()
        names = []
        for i in res:
            names.append(i["name"])
        await ctx.send(messages.name_day_cz.format(name=", ".join(names)))

    @commands.command()
    async def meniny(self, ctx):
        url = config.nameday_sk
        res = requests.get(url).json()
        names = []
        for i in res:
            names.append(i["name"])
        await ctx.send(messages.name_day_sk.format(name=", ".join(names)))

    @commands.command(aliases=['pocasi', 'pocasie'])
    async def weather(self, ctx, *args):
        token = config.weather_token
        city = "Brno"
        if(len(args) != 0):
            city = ' '.join(map(str, args))
        url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&units=metric&lang=cz&appid=" + token
        res = requests.get(url).json()
        
        if(str(res["cod"]) == "200"):
            description = "Aktuální počasí v městě " + res["name"] + ", " + res["sys"]["country"]
            embed=discord.Embed(title="Počasí", description=description)
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
        elif(str(res["cod"]) == "404"):
            await ctx.send("Město nenalezeno")
        elif(str(res["cod"]) == "401"):
            await ctx.send("Rip token")
        else:
            await ctx.send("Město nenalezeno! " + emote.panic + " (" + res["message"] + ")")



def setup(bot):
    bot.add_cog(Librarian(bot))
