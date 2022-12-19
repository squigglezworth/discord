from discord import Bot
import logging


class Bot(Bot):
    def __init__(self, name, *args, **options):
        super().__init__()

        # Setup logging formatter & stream handler
        fmt = logging.Formatter(f"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        fmt.default_msec_format = None
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)

        # Attach handlers to loggers and set logging level
        logger = logging.getLogger("discord")
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        logger = logging.getLogger(f"bot.{name}")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        self.logger = logger

    async def on_application_command(self, ctx):
        self.logger.info(f"{ctx.command} - Responding to {ctx.user}")

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user} on {len(self.guilds)} guilds")

    async def on_guild_join(self, guild):
        self.logger.info(f'Joined guild "{guild.name}"')
