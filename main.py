import json

import discord
from discord.ext import commands

# fmt: off
class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(custom_id='ReactionRoles-Add', min_values=0)
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("Discord thinks you are not a member of this server", ephemeral=True)
        
        roles = [role for role in interaction.user.roles if role.id not in map(lambda o: int(o.value), select.options)]

        for role_id in map(int, select.values):
            role = interaction.guild.get_role(role_id)
            if not role:
                continue
            roles.append(role)

        try:
            await interaction.user.edit(roles=roles)
        except Exception as e:
            await interaction.followup.send(f"Could not add roles: {type(e).__name__} {e}\n\nReport this to the admins", ephemeral=True)
        else:
            await interaction.followup.send('Your roles have been updated.', ephemeral=True)

class RolesBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            help_command=None,
            intents=discord.Intents.default() | discord.Intents(members=True),
        )

        # load config
        with open("bot_config.json", "r") as fp:
            self.config = json.load(fp)

    async def setup_hook(self) -> None:
        self.add_view(RolesView())


bot = RolesBot()


@bot.group(name="load")
@commands.has_permissions(administrator=True)
async def load_waitlist(ctx: commands.Context):
    return


@load_waitlist.command(name="waitlist_notifications")
async def waitlist_notifications(ctx: commands.Context):
    """Loads the waitlist message"""
    config = bot.config['audiophile_and_producer']

    options = []
    for role in config["roles"]:
        options.append(discord.SelectOption(label=role["title"], value=role["id"]))

    view = RolesView()
    view.role_select.options = options
    view.role_select.max_values = len(options)
    view.role_select.placeholder = config['place_holder']
    await ctx.send(config['message_content'], view=view)


bot.run(bot.config["bot_token"])
