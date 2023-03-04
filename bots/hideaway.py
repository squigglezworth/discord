import bot
import discord
import logging
import os
from utils.webhook import WebhookHandler
from discord.ext import commands
from dotenv import load_dotenv
from cogs import colors, memes, roles, publisher, f1

role_settings = {
    "roles": {
        "name": "roles",
        "description": "Add/remove various roles from yourself. Tag them to share links, chat with others, etc",
        # Embed content
        "embed": "*Hello <@{ctx.user.id}>, your current roles are:\n{RolesList}\n\nUse the menus below to add or remove roles\n**Everyone is encouraged to @ping these roles to share things of interest, to find others to play games with, etc***",
        # No limit
        "max_one": 0,
        # List of role IDs to exclude from the listing of the user's current roles
        # @everyone is automatically excluded
        "exclude": [983269188036608050, 637192413584293889],
        "dropdowns": [
            {
                "placeholder": "🎮 Game roles",
                # Set this to 1 to randomize the order of roles for this dropdown
                "randomize": 0,
                "roles": [
                    [690896728953585674, "", "<:warships:787272758354116619>"],
                    [765302061792886815, "", "<:elite:787273549404438528>"],
                    [683056749460062262, "", "<:warframe:787275270578503720>"],
                    [790003154724978688, "", "<:minecraft:790003030925246484>"],
                    [791231782543425536, "", "<:arma3:791231464174780456>"],
                    [791232272007036928, "", "💰"],
                    [819007747801481257, "", "<:fallout:819007399817248789>"],
                    [836707348076167247, "", "<:f1:835693536640761856>"],
                    [843389345485422592, "", "<:starcitizenwhite:843386176001802240>"],
                    [849037771993907201, "", "<:tarkov:849037591718395905>"],
                    [861315460099473439, "", "<:valheim:861315289320259604>"],
                ],
            },
            {
                "placeholder": "EVE Online roles",
                "randomize": 0,
                "roles": [
                    # [<id>, "<description>", "<emoji>"]
                    [
                        786356797429514261,
                        "General EVE Online role",
                        "<:eve:787273908528349204>",
                    ],
                    [1045323484441616384, "Get notified about new corp giveaways", "🎉"],
                    [880572127823159366, "Get pings about mining fleets", "⛏️"],
                    [880572192872611871, "Notifications about PVP fleets", "⚔️"],
                    [
                        885936958394748950,
                        "Help the corp & corp members by hauling goods",
                        "<:freighter:1040091624715341865>",
                    ],
                    [
                        1042294285741084743,
                        "Share info about wormholes and other exploration sites",
                        "<:wormhole:1042298751336861779>",
                    ],
                    [1042294090802417694, "Buy & sell goods in #marketplace", "📈"],
                ],
            },
            {
                "placeholder": "🏳️‍🌈 LGBT roles",
                "randomize": 0,
                "roles": [
                    # [<id>, "<description>", "<emoji>"]
                    [1007573574082642011, "All of these grant access to the #🌈lgbt channel", "<:prideflag:1004829674112811170> "],
                    [1007573880728199188, "", "<:LesbianPride:1007578778035290112> "],
                    [1007573890198949920, "", "<:BisexualPride:1007578776630198303> "],
                    [1007573993135558679, "", "<:prideflag:1004829674112811170> "],
                    [1007575326227972209, "", "<:TransPride:1007578772935024660> "],
                    [1007623293811032157, "", "<:AsexualPride:1007623033189568562> "],
                    [1007623250118987796, "", "<:AromanticPride:1007623034959581245> "],
                    [1007573999699628072, "", "<:male_symbol:1041757493010894958> "],
                    [1007574163302658081, "", "<:female_symbol:1041757820900605972> "],
                    [1007574166242861117, "", "<:TransgenderSymbol:1007581443867815956>"],
                ],
            },
            {
                "placeholder": "Misc/Topic roles",
                "randomize": 0,
                "roles": [
                    # [<id>, "<description>", "<emoji>"]
                    [
                        1037691564954238996,
                        "Grants access to the neurodivergent chat channel",
                        "<:NeurodiversityPride:1037203581733974026>",
                    ],
                    [972970423744610374, "", "<:f1:835693536640761856>"],
                    [972970633174614058, "", "📚"],
                    [1020370146063286423, "Visit the #book-club channel to share what you're reading!", "📖"],
                    [972970544670584852, "", "🎬"],
                ],
            },
        ],
    },
    "icons": {
        # /role <name>
        "name": "icons",
        # Command description
        "description": "Stand out with a fancy icon that will appear next to your name in chat",
        # Embed content
        "embed": "*Hello <@{ctx.user.id}>, your current icon role is {ShortRolesList}\n\nSelect one below, and it'll show up next to your name in chat!*",
        # Allow only 1 of *all* the provided roles
        "max_one": 1,
        # List of role IDs to exclude from the listing of the user's current roles
        # @everyone is automatically excluded
        "exclude": [],
        "dropdowns": [
            {
                "placeholder": "🦉 Animal Icons",
                "randomize": 0,
                "roles": [
                    [1041543542423691336, "", "🦑"],
                    [1042254987855679568, "", "<:blue_octopus2:1042254458882637876>"],
                    [1042252793739739206, "", "🐙"],
                    [1041543751845290024, "", "🐳"],
                    [1041543812272623737, "", "🦀"],
                    [1041719288437944410, "", "🦉"],
                    [1041726074775687279, "", "<:redpanda:1041725947243675729>"],
                    [1041726257957703791, "", "🐱"],
                    [1041726321480454275, "", "🐶"],
                ],
            },
            {
                "placeholder": "🏳️‍🌈 LGBT Icons",
                "randomize": 0,
                "roles": [
                    [1041321819984105512, "", "<:LesbianPride:1007578778035290112>"],
                    [1041321894927937646, "", "<:GayPride:1007578774897954867>"],
                    [1041321919984713848, "", "<:BisexualPride:1007578776630198303>"],
                    [1041321940998168627, "", "🏳️‍⚧️"],
                    [1041321961697071214, "", "<:male_symbol:1041757493010894958>"],
                    [1041322000469196850, "", "<:female_symbol:1041757820900605972>"],
                    [
                        1041322026234822716,
                        "",
                        "<:TransgenderSymbol:1007581443867815956>",
                    ],
                    [1041322212982018059, "", "<:AsexualPride:1007623033189568562>"],
                    [1041322264815218688, "", "<:AromanticPride:1007623034959581245>"],
                ],
            },
            {
                "placeholder": "🥐 Misc. Icons",
                "randomize": 0,
                "roles": [
                    [1041322728365506620, "", "<:logo:875904386444967946>"],
                    [1041322473783840888, "", "<:corplogo:787272419127722004>"],
                    [
                        1041322146636513360,
                        "",
                        "<:NeurodiversityPride:1037203581733974026>",
                    ],
                    [1041322094543261716, "", "<:freighter:1040091624715341865>"],
                    [1041322195701481502, "", "📚"],
                    [1041335138434424942, "", "🥐"],
                    [1042121441891582002, "", "💥"],
                    [1043172047108440104, "", "<:blueverified:1054604704304336927>"],
                    [1054605750070161459, "", "<:bluedoubleverified:1054604705638121492>"],
                    [1054605825534074900, "", "<:goldverified:1054603064876736632>"],
                    [1054606008598679584, "", "<:doublegoldverified:1054603066608996362>"],
                ],
            },
        ],
    },
}

load_dotenv()

TOKEN = os.getenv("DEBUG_TOKEN") if os.getenv("DEBUG") == "True" else os.getenv("PROD_TOKEN")
GUILDS = [int(g) for g in os.getenv("GUILDS").split(",")] if os.getenv("GUILDS") else []

# Hideaway bot
intents = discord.Intents.default()
intents.guilds = True
bot = bot.Bot("hideaway", intents=intents, debug_guilds=GUILDS)
# Roles cog
roles = roles.Roles(bot, role_settings)
# Color roles cog
color_prefix = "[C]"
bot.add_cog(colors.Colors(bot, color_prefix))
# F1 Notification cog
db = os.getenv("F1_DB") or "f1.sqlite"
channel = os.getenv("F1_CHANNEL")
perm_channel = os.getenv("F1_PERMCHANNEL")
role = os.getenv("F1_ROLE")
bot.add_cog(f1.F1(bot, db, role, channel, perm_channel))

# Setup webhook logging
log_webhook = os.getenv("LOG_WEBHOOK")
if log_webhook:
    handler = WebhookHandler(log_webhook, color=0x0FF5338)
    fmt = logging.Formatter(f"%(name)s - %(levelname)s - %(message)s")
    fmt.default_msec_format = None
    handler.setFormatter(fmt)
    handler.setLevel(logging.INFO)

    logging.getLogger("discord").addHandler(handler)
    bot.logger.addHandler(handler)

# Setup & register /customize


class Button(discord.ui.Button):
    def __init__(self, ctx, options, buttons=None):
        self.ctx = ctx
        self.buttons = buttons
        global role_settings
        self.role_settings = role_settings

        super().__init__(label=options[0], style=options[2], custom_id=options[1])

    async def callback(self, interaction):
        """
        Callback for /customize buttons
        """
        buttons = [Button(self.ctx, b, self.buttons) for b in self.buttons]

        if self.custom_id in ["roles", "icons"]:
            embed, view = roles.Message(ctx=self.ctx, updates=None, menu=self.role_settings[self.custom_id], extras=buttons)
        if self.custom_id == "colors":
            cog = bot.get_cog("Colors")
            embed, view = cog.Message(interaction, ExtraViews=buttons)

        for b in buttons:
            view.add_item(b)

        await interaction.response.edit_message(embed=embed, view=view)


async def customize(ctx):
    """
    Personalize your presence in the server - change the color of your name, add an icon, and more!
    """
    buttons = [
        ["🥐 Roles", "roles", discord.ButtonStyle.blurple],
        ["🌈 Change your color", "colors", discord.ButtonStyle.green],
        ["🚩 Select an icon", "icons", discord.ButtonStyle.blurple],
    ]

    view = discord.ui.View()

    for b in buttons:
        view.add_item(Button(ctx, b, buttons))

    embed = discord.Embed(
        color=0x299AFF,
        description="*Use the buttons below to personalize your presence in the server. Give yourself roles to share things with other members. Add an icon that displays next to your name. Give yourself a fancy color. The possibilities are nearly endless!*",
    )

    await ctx.respond(ephemeral=True, embed=embed, view=view)


command = discord.SlashCommand(
    customize,
    name="customize",
    description="Personalize your presence in the server - change the color of your name, add an icon, and more!",
)

bot.add_application_command(command)


bot.logger.info(f"Registering /customize")


bot.run(TOKEN)
