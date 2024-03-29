import math
import logging
import discord
from discord.ext import commands
from sqlitedict import SqliteDict


YES_EMOJI = "<:yes:1052475891235692544>"
NO_EMOJI = "<:no:1052475925759008778>"
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


def remove_from_db(db, guild, channels):
    """
    Utility function to remove channels from the current guilds tracked channels
    """
    with SqliteDict(db, tablename=str(guild.id)) as db:
        if guild.id in db:
            db[guild.id] = [c for c in db[guild.id] if c not in channels]

        db.commit()

        return db[guild.id]


def add_to_db(db, guild, channels):
    """
    Utility function to add channels to the current guilds tracked channels
    """
    with SqliteDict(db, tablename=str(guild.id)) as db:
        if guild.id in db:
            db[guild.id] += channels
        else:
            db[guild.id] = channels

        db.commit()

        return db[guild.id]


class AutoPublisher(commands.Cog):
    settings = []

    def __init__(self, bot, db):
        bot.logger.info(f"Registering /publisher")

        self.logger = bot.logger
        self.db = db
        self.bot = bot

    @commands.slash_command()
    async def publisher(self, ctx):
        """
        Configure auto-publishing settings for Announcement channels
        """
        if not ctx.channel.permissions_for(ctx.user).manage_channels:
            return await ctx.respond("*You need the **Manage Channels** permission to use this command*", ephemeral=True)

        with SqliteDict(self.db, tablename=str(ctx.guild.id)) as db:
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
            with SqliteDict(self.db, tablename=str(message.guild.id)) as db:
                if message.guild.id in db:
                    self.settings = db[message.guild.id]

        if message.channel.id in self.settings:
            self.logger.info(f"publisher - Publishing message from '#{message.channel.name}' on '{message.guild.name}'")

            try:
                await message.publish()
            except discord.Forbidden:
                self.logger.warning(f"publisher - Missing permissions for '#{message.channel.name}' on '{message.guild.name}'")
            except dicsord.HTTPException:
                self.logger.warning(f"publisher - Publishing failed for '#{message.channel.name}' on '{message.guild.name}'")

    def Message(self, ctx):
        """
        Assemble the message (content, embed, and/or view)
        """
        content = ""
        channels = []
        i = 1

        for c in ctx.guild.text_channels:
            if c.is_news():
                perms = c.permissions_for(ctx.me)
                if perms.manage_messages and perms.send_messages:
                    channel = [c, 1]
                else:
                    channel = [c, 0]
                channels += [channel]

                content += f"{EMOJI[i]} —  "

                if c.id in self.settings:
                    content += YES_EMOJI
                else:
                    content += NO_EMOJI

                content += f" <#{c.id}>"
                if not channel[1]:
                    content += " \* *Missing permissions for this channel*"
                content += "\n"
                i += 1

        self.channels = channels

        view = View(self, ctx)

        if len(channels) == 0:
            content = "*No [Announcement](https://support.discord.com/hc/en-us/articles/360032008192-Announcement-Channels-) channels configured!*"
            # Remove Enable/Disable buttons
            view.children = []

        embed = discord.Embed(description=content, color=0x0299AFF)
        return {"embed": embed, "view": view}


class View(discord.ui.View):
    """
    The View holds components like buttons
    """

    def __init__(self, cog, ctx):
        super().__init__()

        self.cog = cog
        self.ctx = ctx
        self.channels = cog.channels
        self.db = cog.db

        for i, c in enumerate(self.channels):
            self.add_item(ChannelButton(i + 1, ctx, cog))

    @discord.ui.button(label="Enable for All", style=discord.ButtonStyle.success)
    async def EnableButton(self, button, interaction):
        self.cog.logger.info(f"publisher - Enabling auto-publishing for all channels on '{self.ctx.guild.name}'")

        settings = add_to_db(self.db, self.ctx.guild, [c[0].id for c in self.channels])
        self.cog.settings = settings

        message = self.cog.Message(self.ctx)
        await interaction.response.edit_message(**message)

    @discord.ui.button(label="Disable for All", style=discord.ButtonStyle.red)
    async def DisableButton(self, button, interaction):
        self.cog.logger.info(f"publisher - Disabling auto-publishing for all channels on '{self.ctx.guild.name}'")

        settings = remove_from_db(self.db, self.ctx.guild, [c[0].id for c in self.channels])
        self.cog.settings = settings

        message = self.cog.Message(self.ctx)
        await interaction.response.edit_message(**message)


class ChannelButton(discord.ui.Button):
    """
    Handles button clicks to toggle specific channels
    """

    def __init__(self, index, ctx, cog):
        self.ctx = ctx
        self.cog = cog
        self.db = cog.db

        channel = cog.channels[index - 1][0]
        style = discord.ButtonStyle.green
        if channel.id in self.cog.settings:
            style = discord.ButtonStyle.red

        super().__init__(custom_id=str(index), label=str(index), style=style, row=math.ceil(index / 5))

    async def callback(self, interaction):
        channel = self.cog.channels[int(interaction.custom_id) - 1][0]
        self.cog.logger.info(f"publisher - Toggling publishing for '{channel.name}' on '{channel.guild.name}'")

        if channel.id in self.cog.settings:
            settings = remove_from_db(self.db, interaction.guild, [channel.id])
            self.cog.settings = settings
        else:
            settings = add_to_db(self.db, interaction.guild, [channel.id])
            self.cog.settings = settings

        message = self.cog.Message(self.ctx)
        await interaction.response.edit_message(**message)
