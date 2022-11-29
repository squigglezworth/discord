import discord, re, logging
from discord.ext import commands
from imdb import Cinemagoer, IMDbError
from retry import retry

logger = logging.getLogger("bot.imdb")


@retry(tries=5)
def search_movie(search):
    imdb = Cinemagoer()
    results = imdb.search_movie(search)

    if not len(results):
        raise IMDbError
    else:
        return results


def update_movie(result):
    info = ["main", "plot"]
    imdb = Cinemagoer()

    return imdb.update(result, info)


class Imdb(commands.Cog):
    def __init__(self, bot, guilds=None):
        logger.info(f"Registering /imdb" + (f" on {len(guilds)} guilds" if guilds else " globally"))

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
        imdb = Cinemagoer()

        if re.match("^\d+$", search.lstrip("tt")):
            await ctx.interaction.response.defer(ephemeral=False)

            self.results = [imdb.get_movie(search.lstrip("tt"))]
            content = f"<@{ctx.user.id}>"
        else:
            await ctx.interaction.response.defer(ephemeral=True)

            try:
                self.results = search_movie(search)
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
            view = View(cog, ctx, results)
            embed.description = "Select a movie to send in the current channel:\n"

            for i in range(0, 5):
                url = f"https://imdb.com/title/tt{self.results[i].movieID}"
                embed.description += f"{i+1}) ***[{self.results[i]}]({url})*** ({self.results[i].get('year')})\n"
        elif len(results) == 1:
            result = results[0]
            update_movie(result)

            embed.title = f"***{result['title']}*** "
            if result["kind"] == "tv series":
                embed.title += f"(TV show ∙ {result['series years']})"
            else:
                embed.title += f"({result['year']})"

            embed.url = f"https://imdb.com/title/tt{result.movieID}"
            embed.set_thumbnail(url=result["full-size cover url"])

            if "plot" in result:
                embed.description = result["plot"][0]
            else:
                embed.description = "No Plot :("

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
        else:
            embed.description = "Uh oh, something went wrong! Please let <@267869612383666177> know!"

        embed.set_footer(text="Use /imdb to lookup TV/movies", icon_url="https://cdn.discordapp.com/attachments/525755278172356625/1046961975416066118/image.png")
        return embed, view


class View(discord.ui.View):
    def __init__(self, cog, ctx, results=[]):
        super().__init__()

        if len(results) > 1:
            for i in range(0, 5):
                self.add_item(Button(cog, ctx, i, results))


class Button(discord.ui.Button):
    def __init__(self, cog, ctx, index, results):
        self.cog = cog
        self.ctx = ctx

        super().__init__(
            label=index + 1,
            custom_id=results[index].movieID,
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
