import discord
from discord import app_commands
from discord.ext import commands

from .ctftime import get_ctftime_informations

class Handler():
    def __init__(self, client: commands.Bot, ctfbot) -> None:
        self.ctfclient = client
        self.ctfbot = ctfbot
        self.register_commands()

    def register_commands(self):
        @self.ctfclient.tree.command(
            name="create_ctf",
            description="Create a new CTF category with channels"
        )
        @app_commands.describe(ctfname="The name of the CTF" ,
                               ctftime="Optional: CTFTime Event URL (https://ctftime.org/event/XXXX) for CTF informations")
        async def create_ctf(interaction: discord.Interaction, ctfname: str, ctftime: str = None):
            await self.create_ctf(interaction, ctfname, ctftime=ctftime)

        @self.ctfclient.tree.command(
            name="delete_ctf",
            description="Delete an existing CTF and all its channels"
        )
        @app_commands.describe(ctfname="The name of the CTF to delete")
        async def delete_ctf(interaction: discord.Interaction, ctfname: str):
            await self.delete_ctf(interaction, ctfname)

    async def create_ctf(self, interaction: discord.Interaction, ctf_name: str, ctftime:str = None):
        
        guild = interaction.guild
        err=None

        overwrites = None
        if self.ctfbot.require_role:
            active_ctf_role = discord.utils.get(guild.roles, name=self.ctfbot.require_role_name)
            if not active_ctf_role:
                await interaction.response.send_message(f'Required role ({self.ctfbot.require_role_name}) for CTF room not found. Are you sure this role exists?', ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                active_ctf_role: discord.PermissionOverwrite(view_channel=True)
            }

        existing_category = discord.utils.get(guild.categories, name=ctf_name)
        if existing_category:
            await interaction.response.send_message(f"CTF '{ctf_name}' already exists.")
            return

        category = await guild.create_category(ctf_name, overwrites=overwrites)
        await guild.create_voice_channel(f'General-{ctf_name}', category=category, overwrites=overwrites)

        if ctftime:
            informations,err = get_ctftime_informations(ctftime)
            information_channel = await guild.create_text_channel("CTF-Informations", category=category, overwrites=overwrites)
            if len(informations.keys()) > 0:
                message = "**CTF Information**\n\n"
                for key, value in informations.items():
                    message += f"**{key.capitalize()}**: {value}\n"
                await information_channel.send(message)
                
        for channel in self.ctfbot.ctf_channels:
            await guild.create_text_channel(channel, category=category, overwrites=overwrites)

        if not err:
            await interaction.response.send_message(f'CTF {ctf_name} has been created!')
        else:
            await interaction.response.send_message(f'CTF {ctf_name} has been created but errors occured : ERR={err}')

    async def delete_ctf(self, interaction: discord.Interaction, ctf_name: str):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=ctf_name)

        if not category:
            await interaction.response.send_message(f'CTF {ctf_name} not found.', ephemeral=True)
            return

        for channel in category.channels:
            await channel.delete()

        await category.delete()
        await interaction.response.send_message(f'CTF {ctf_name} has been deleted')
