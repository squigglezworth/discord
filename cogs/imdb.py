import discord, re, logging
from discord.ext import commands
from imdb import Cinemagoer, IMDbError
from retry import retry

logger = logging.getLogger("bot.imdb")


@retry(tries=5)
def search_movie(search, db=None):
    if db:
        logger.info(f"Searching for {search} using sqlite ...")
        imdb = Cinemagoer("s3", db)
    else:
        logger.info(f"Searching for {search} ...")
        imdb = Cinemagoer()

    results = imdb.search_movie(search, results=5)

    # Sometimes it returns an empty list!
    if not len(results):
        # Raise an exception so @retry can do its thing
        raise IMDbError
    else:
        logger.info("Done!")
        return results


@retry(tries=5)
def update_movie(result, db=None):
    if db:
        logger.info(f"Updating info for {result} using sqlite ...")
        imdb = Cinemagoer("s3", db)
    else:
        logger.info(f"Updating info for {result} ...")
        imdb = Cinemagoer()

    logger.info(f"Done!")
    return imdb.update(result)


@retry(tries=5)
def get_movie(result, db=None):
    if db:
        logger.info(f"Getting info for {result} using sqlite ...")
        imdb = Cinemagoer("s3", db)
    else:
        logger.info(f"Getting info for {result} ...")
        imdb = Cinemagoer()

    logger.info(f"Done!")
    return imdb.get_movie(result)


class Imdb(commands.Cog):
    def __init__(self, bot, db=None):
        self.db = db
        logger.info(f"Registering /imdb")

        bot.add_application_command(
            discord.SlashCommand(
                self.CommandCallback,
                name="imdb",
                description="Look stuff up on IMDb",
                options=[
                    discord.Option(
                        str,
                        name="search",
                        description="What to search for. Enter a movie/TV show name or an IMDb ID (e.g. 'The Matrix', tt0133093, 0133093)",
                    )
                ],
            )
        )

    async def CommandCallback(self, ctx, search: str):
        if re.match("^\d+$", search.lstrip("tt")):
            # Handle IMDb IDs (tt1234567, 1234567)
            await ctx.interaction.response.defer(ephemeral=False)

            self.results = [get_movie(search.lstrip("tt"))]
            content = f"<@{ctx.user.id}>"
        else:
            # Handle a normal search
            await ctx.interaction.response.defer(ephemeral=True)

            try:
                self.results = search_movie(search, self.db)
            except:
                self.results = []
            content = ""

        embed, view = self.Message(ctx, self)

        await ctx.respond(content=content, embed=embed, view=view)

    def Message(self, ctx, cog):
        embed = discord.Embed(color=0x299AFF)
        view = View(cog, ctx)
        results = self.results

        if len(results) > 1:
            logger.info("Search found; letting user choose")

            view = View(cog, ctx, results)
            embed.description = "Select a movie to send in the current channel:\n"

            for i, result in enumerate(results):
                logger.info(f"Building embed for movie #{i+1}")

                update_movie(result, self.db)

                url = f"https://imdb.com/title/tt{result.movieID}"
                embed.description += f"{i+1}) ***[{result}]({url})*** ({result['year']})"

                if "creator" in result:
                    embed.description += f" - *Created by: {result['creator'][0]['name']}*"
                elif "director" in result:
                    embed.description += f" - *Directed by: {result['director'][0]['name']}*"

                embed.description += "\n"

        elif len(results) == 1:
            result = results[0]
            # Even when an sqlite database is available, update the final result via the website
            # Otherwise, the cover URL will not be available
            update_movie(result)

            # Build the embed
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
        else:
            # If search_movie failed ...
            embed.description = "Uh oh, something went wrong! Please let your admin know!"

        return embed, view


class View(discord.ui.View):
    def __init__(self, cog, ctx, results=[]):
        super().__init__()

        # If there's only one result, we don't need any buttons
        if len(results) > 1:
            for i in range(0, 5):
                self.add_item(Button(cog, ctx, i, results))


class Button(discord.ui.Button):
    def __init__(self, cog, ctx, index, results):
        self.cog = cog
        self.ctx = ctx

        super().__init__(
            label=index + 1,
            custom_id=str(results[index].movieID),
            style=discord.ButtonStyle.success,
        )

    async def callback(self, interaction):
        """
        Callback for buttons
        """

        imdb = Cinemagoer()
        result = imdb.get_movie(self.custom_id)
        self.cog.results = [result]

        embed, view = self.cog.Message(interaction, self.cog)

        await self.ctx.channel.send(content=f"<@{self.ctx.user.id}>", embed=embed, view=view)
        await self.ctx.delete()
