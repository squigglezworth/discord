import discord
from discord.ext import commands


class Publisher(commands.Cog):
    def __init__(self, bot):
        bot.logger.info(f"Registering /publisher")

        self.logger = bot.logger
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.is_news():
            self.logger.info(f"publisher - Publishing message from '#{message.channel.name}' on '{message.guild.name}'")

            try:
                await message.publish()
            except discord.Forbidden:
                self.logger.warning(f"publisher - Missing permissions for '#{message.channel.name}' on '{message.guild.name}'")
            except dicsord.HTTPException:
                self.logger.warning(f"publisher - Publishing failed for '#{message.channel.name}' on '{message.guild.name}'")
