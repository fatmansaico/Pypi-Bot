import itertools
import random
from typing import Optional
from aiohttp import request
import aiohttp
import lightbulb
import hikari
import requests
from lightbulb import commands, Context
from discord.utils import escape_markdown
from ..bot import Bot



class Pypi(lightbulb.Plugin):
    
    @commands.group(name="pypi")
    async def pypi_group(self, ctx: "Context") -> None:
        await ctx.respond("Pypi commands: packageinfo, size, name, version")

    @pypi_group.command(name="packageinfo")
    async def packageinfo(self, ctx: "Context", package: str):
        self.http_session = aiohttp.ClientSession()
        embed = hikari.Embed(title="", colour=hikari.Color.from_rgb(0,255,255))
        
        URL = "https://pypi.org/pypi/{package}/json"
        PYPI_COLOURS = itertools.cycle(((255,255,0), (51, 0, 255), (255, 255, 255)))

        async with self.http_session.get(URL.format(package=package)) as response:
            if response.status == 404:
                embed.description = "Package could not be found."

            elif response.status == 200 and response.content_type == "application/json":
                response_json = await response.json()
                info = response_json["info"]

                embed.title = info["name"] + " " + info["version"]
                embed.url = info["package_url"]
                embed.colour = next(PYPI_COLOURS)

                summary = escape_markdown(info["summary"])

                # Summary could be completely empty, or just whitespace.
                if summary and not summary.isspace():
                    embed.description = summary
                else:
                    embed.description = "No summary provided."

            else:
                embed.description = "There was an error when fetching your PyPi package."
                print(f"Error when fetching PyPi package: {response.status}.")

        await ctx.respond(embed=embed)


def load(bot: "Pypi") -> None:
    bot.add_plugin(Pypi())


def unload(bot: "Pypi") -> None:
    bot.remove_plugin("Pypi")