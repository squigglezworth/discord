import discord
import re
import logging
import sqlite3
from discord.ext import commands
from imdb import Cinemagoer

logger = logging.getLogger("bot.imdb")


class Imdb(commands.Cog):
    def __init__(self, bot, db):
        logger.info("Preparing /imdb...")
        self.bot = bot
        self.db = db

        stmt = """
        SELECT primaryTitle, startYear, title_basics.tconst, numVotes
        FROM title_basics
        LEFT JOIN title_ratings ON title_basics.tconst = title_ratings.tconst
        WHERE numVotes > 0
        ORDER BY numVotes DESC
        """
        con = sqlite3.connect(db[10:])
        cur = con.execute(stmt)
        results = cur.fetchall()

        titles = [[f"{r[0]} - {r[1]}", r[2]] for r in results]
        self.titles = titles

        option = discord.Option(str, name="search", description="What to search for. Begin typing to search, or enter an IMDb ID (e.g. tt0133093, 0133093)", autocomplete=self.imdb_autocomplete)

        bot.add_application_command(
            discord.SlashCommand(
                self.imdb,
                name="imdb",
                description="Look stuff up on IMDb",
                options=[option],
            )
        )

        logger.info(f"Registering /imdb")

    async def imdb(self, ctx, search):
        await ctx.interaction.response.defer()
        if re.match("^\d+$", search.lstrip("tt")):
            imdb = Cinemagoer()
            result = imdb.get_movie(search)
            imdb.update(result)

            # Build the embed
            embed = discord.Embed(color=0x299AFF)
            embed.title = f"***{result['title']}*** "
            if result["kind"] == "tv series":
                embed.title += f"(TV show ∙ {result['series years']})"
            else:
                embed.title += f"({result['year']})"

            embed.url = f"https://imdb.com/title/tt{result.movieID}"

            if "full-size cover url" in result.keys():
                embed.set_thumbnail(url=result["full-size cover url"])

            if "plot" in result:
                embed.description = result["plot"][0]
            else:
                embed.description = "No Plot :("

            # Build links to various peoples' IMDb pages and add them to the embed description
            embed.description += "\n\n"
            if "creator" in result:
                creators = []
                for c in result["creator"]:
                    creators += [f"[{c['name']}](https://imdb.com/name/nm{c.personID})"]
                embed.description += f"*Created by: {', '.join(creators)}*\n"
            if "director" in result:
                directors = []
                for d in result["director"]:
                    directors += [f"[{d['name']}](https://imdb.com/name/nm{d.personID})"]
                embed.description += f"*Directed by: {', '.join(directors)}*\n"
            if "cast" in result:
                cast = []
                n = 5  # Show 5 cast members at most
                for c in result["cast"][:n]:
                    cast += [f"[{c['name']}](https://imdb.com/name/nm{c.personID})"]
                embed.description += f"*Starring: {', '.join(cast)}*"

            embed.set_footer(
                text="Use /imdb to lookup TV/movies",
                icon_url="https://cdn.discordapp.com/attachments/525755278172356625/1046961975416066118/image.png",
            )

            await ctx.respond(embed=embed)
        else:
            await ctx.respond(ephemeral=True, content="Please select an option from the lsit, or provide an IMDb ID")

    async def imdb_autocomplete(self, ctx):
        await ctx.interaction.response.defer()

        if len(ctx.value) == 0:
            return ["Begin typing to search for a movie..."]
        if len(ctx.value) < 5:
            return ["Keep typing..."]

        results = [r for r in self.titles if ctx.value in r[0]][:10]

        choices = []
        for r in results:
            choice = discord.OptionChoice(name=r[0][:100], value=str(r[1]))
            choices += [choice]

        if choices:
            return choices
        else:
            return ["No results found! Make sure you spelled it right, or try entering an IMDb ID"]
