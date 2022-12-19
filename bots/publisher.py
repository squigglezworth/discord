import bot
import discord
import os
from dotenv import load_dotenv
from cogs import publisher

load_dotenv()
TOKEN = os.getenv("PUBLISHER_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
bot = bot.Bot("publisher", intents=intents)

bot.add_cog(publisher.AutoPublisher(bot))


bot.run(TOKEN)
