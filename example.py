menus = {
    "roles": {
        # The name of the command
        "name": "roles",
        "description": "Add/remove various roles from yourself. Tag them to share links, chat with others, etc",
        # Embed content
        "embed": "*Hello <@{ctx.user.id}>, your current roles are:\n{RolesList}\n\nUse the menus below to add or remove roles.*",
        # If you set this to 1, users will only be able to have 1 of the roles provided
        # This can be useful for e.g. allowing users to select a role icon role
        "max_one": 0,
        # List of role IDs to exclude from the listing of the user's current roles (RolesList) in the embed
        # @everyone is automatically excluded
        "exclude": [ ... ],
        # Define up to 5 dropdowns that'll be shown for this menu
        "dropdowns": [
            {
                "placeholder": "Dropdown 1",
                # Set this to 1 to randomize the order of roles for this dropdown
                "randomize": 0,
                "roles": [
                    # Define up to 25 roles for this dropdown
                    # The roles must exist on the server. The name will be used as the entry in the dropdown
                    # The description will be shown under the role name in the dropdown
                    # The emoji can be a Unicode emoji, or a custom emoji (<:name:id>)
                    # [<id>, "<description>", "<emoji>"],
                    # [<id>, "<description>", "<emoji>"],
                    # ...
                ]
            },
            {
                "placeholder": "Dropdown 2",
                "randomize": 1,
                "roles": [ ... ]
            }
        ]
    },
    "auto_populate example": {
        "name": "example",
        "description": "Another example",
        "embed": "",
        "max_one": 1,
        "exclude": [],
        "auto_populate": {
            "match": ".*",
            "prefix": "[C]",
            "suffix": "",
        },
        "dropdowns": [
        ]
    }
}

import discord, RoleMenus
from cogs import colors, memes, imdb

bot = discord.Bot()

# RoleMenus.py
RoleMenus.register(bot, menus)

# cogs/colors.py
color_prefix = "[C]"
bot.add_cog(colors.Colors(bot, color_prefix))

# cogs/imdb.py
# I highly recommend using the imdb-dataset.sh script to generate a local copy of the IMDb dataset
# This will increase reliability & speed of this command
db = 'sqlite:///imdb.sqlite'
bot.add_cog(imdb.Imdb(bot, db))

# cogs/memes.py
bot.add_cog(memes.Memes(bot))

bot.run(<TOKEN>)
