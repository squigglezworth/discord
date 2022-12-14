import math, logging
import discord
from discord.ext import commands
from sqlitedict import SqliteDict

logger = logging.getLogger("bot.publisher")

YES_EMOJI = "<:yes:1039720761767768204>"
NO_EMOJI = "<:no:1039720760652079224>"
EMOJI = [
    "<:0:1051949928143925279>",
    "<:1:1051949989984747610>",
    "<:2:1051949939208499291>",
    "<:3:1051949988466413578>",
    "<:4:1051949937102946334>",
    "<:5:1051949936012447744>",
    "<:6:1051949934896762990>",
    "<:7:1051949933642649641>",
    "<:8:1051949932199809115>",
    "<:9:1051949930761171005>",
    "<:10:1051949929582579782>",
]


def remove_from_db(guild, channels):
    """
    Utility function to remove channels from the current guilds tracked channels
    """
    with SqliteDict("publisher.sqlite", tablename=str(guild.id)) as db:
        if guild.id in db:
            db[guild.id] = [c for c in db[guild.id] if c not in channels]

        db.commit()

        return db[guild.id]


def add_to_db(guild, channels):
    """
    Utility function to add channels to the current guilds tracked channels
    """
    with SqliteDict("publisher.sqlite", tablename=str(guild.id)) as db:
        if guild.id in db:
            db[guild.id] += channels
        else:
            db[guild.id] = channels

        db.commit()

        return db[guild.id]


class AutoPublisher(commands.Cog):
    settings = []

    def __init__(self, bot, guilds=None):
        self.bot = bot

        logger.info(f"Registering /publisher" + (f" on {len(guilds)} guilds" if guilds else " globally"))

    @commands.slash_command()
    async def publisher(self, ctx):
        """
        Configure auto-publishing settings for Announcement channels
        """
        if not ctx.channel.permissions_for(ctx.user).manage_channels:
            return await ctx.respond("*You need the **Manage Channels** permission to use this command*", ephemeral=True)

        with SqliteDict("publisher.sqlite", tablename=str(ctx.guild.id)) as db:
            if ctx.guild.id in db:
                self.settings = db[ctx.guild.id]

        message = self.Message(ctx)

        await ctx.respond(**message, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listens for messages and publishes them when necessary
        """
        if message.author == self.bot.user:
            return

        if not self.settings:
            with SqliteDict("publisher.sqlite", tablename=str(message.guild.id)) as db:
                if message.guild.id in db:
                    self.settings = db[message.guild.id]

        if message.channel.id in self.settings:
            logger.info(f'Publishing message from "{message.channel.name}"')
            await message.publish()

    def Message(self, ctx):
        """
        Assemble the message (content, embed, and/or view)
        """
        content = ""
        channels = []
        i = 1

        for c in ctx.guild.text_channels:
            if c.is_news():
                channels += [c]
                content += f"{EMOJI[i]} —  "

                if c.id in self.settings:
                    content += YES_EMOJI
                else:
                    content += NO_EMOJI

                content += f" <#{c.id}>\n"
                i += 1

        self.channels = channels

        view = View(self, ctx)

        if len(channels) == 0:
            content = "*No [Announcement](https://support.discord.com/hc/en-us/articles/360032008192-Announcement-Channels-) channels configured!*"
            # Remove Enable/Disable buttons
            view.children = []

        return {"content": content, "view": view}


class View(discord.ui.View):
    """
    The View holds components like buttons
    """

    def __init__(self, cog, ctx):
        super().__init__()

        self.cog = cog
        self.ctx = ctx
        self.channels = cog.channels

        for i, c in enumerate(self.channels):
            self.add_item(ChannelButton(i + 1, cog))

    @discord.ui.button(label="Set for All", style=discord.ButtonStyle.success)
    async def EnableButton(self, button, interaction):
        logger.info("Enabling auto-publishing for all channels")

        settings = add_to_db(self.ctx.guild, [c.id for c in self.channels])
        self.cog.settings = settings

        message = self.cog.Message(interaction)
        await interaction.response.edit_message(**message)

    @discord.ui.button(label="Disable for All", style=discord.ButtonStyle.red)
    async def DisableButton(self, button, interaction):
        logger.info("Disabling auto-publishing for all channels")

        settings = remove_from_db(self.ctx.guild, [c.id for c in self.channels])
        self.cog.settings = settings

        message = self.cog.Message(interaction)
        await interaction.response.edit_message(**message)


class ChannelButton(discord.ui.Button):
    """
    Handles button clicks to toggle specific channels
    """

    def __init__(self, index, cog):
        self.cog = cog

        super().__init__(custom_id=str(index), label=str(index), style=discord.ButtonStyle.grey, row=math.ceil(index / 5))

    async def callback(self, interaction):
        channel = self.cog.channels[int(interaction.custom_id) - 1]
        logger.info(f'Toggling "{channel.name}"')

        if channel.id in self.cog.settings:
            settings = remove_from_db(interaction.guild, [channel.id])
            self.cog.settings = settings
        else:
            settings = add_to_db(interaction.guild, [channel.id])
            self.cog.settings = settings

        message = self.cog.Message(interaction)
        await interaction.response.edit_message(**message)
