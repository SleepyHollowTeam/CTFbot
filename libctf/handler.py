import discord
from discord import app_commands
from discord.ext import commands
import asyncio

import logging
logging.basicConfig(level=logging.DEBUG)

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

        @self.ctfclient.tree.command(
            name="join_ctf",
            description="Join an existing CTF"
        )
        @app_commands.describe(ctfname= "CTFname to join",
                               password="Password/Token to join the CTF")
        async def join_ctf(interaction: discord.Interaction, ctfname:str, password: str):
            await self.join_ctf(interaction, ctfname, password)

        @self.ctfclient.tree.command(
            name="link_ctftime",
            description="Link Ctftime event with a ctf"
        )
        @app_commands.describe(ctfname="The name of the CTF" ,
                               ctftime="CTFTime Event URL (https://ctftime.org/event/XXXX) for CTF informations")
        async def link_ctftime(interaction: discord.Interaction, ctfname: str, ctftime:str):
            await self.link_ctftime(interaction, ctfname, ctftime=ctftime)

        @self.ctfclient.tree.command(
            name="unregister",
            description="Remove CTF Role from all users"
        )
        @app_commands.describe()
        async def unregister_command(interaction: discord.Interaction):
            await self.unregister(interaction)

    async def create_ctf(self, interaction: discord.Interaction, ctf_name: str, ctftime:str = None):
        
        guild = interaction.guild
        err=None

        if self.ctfbot.require_role_cmd_name:
            is_admin = discord.utils.get(guild.roles, name=self.ctfbot.require_role_cmd_name)
            if not is_admin:
                await interaction.response.send_message(f'Required role ({self.ctfbot.require_role_cmd_name}) for creating CTF not found. Are you sure this role exists?', ephemeral=True)
                return
            
            can_run = False
            for role in interaction.user.roles:
                if self.ctfbot.require_role_cmd_name == role.name:
                    can_run = True
            if not can_run:
                await interaction.response.send_message(f'You do not have the required role ({self.ctfbot.require_role_cmd_name}) to create a CTF.', ephemeral=True)
                return
            
        overwrites = None
        if self.ctfbot.require_role_name:
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
        await guild.create_voice_channel(f'General-CTF', category=category, overwrites=overwrites)

        if ctftime:
            informations,err = await get_ctftime_informations(ctftime)
            information_channel = await guild.create_text_channel("ctf-informations", category=category, overwrites=overwrites)
            if informations:
                await information_channel.send(informations)

        tasks = []
        for channel in self.ctfbot.ctf_channels:
            tasks.append(asyncio.create_task(guild.create_text_channel(channel, category=category, overwrites=overwrites)))
        await asyncio.gather(*tasks)
        if not err:
            await interaction.response.send_message(f'CTF {ctf_name} has been created!')
        else:
            await interaction.response.send_message(f'CTF {ctf_name} has been created but errors occured : ERR={err}')


    async def link_ctftime(self, interaction: discord.Interaction, ctf_name: str, ctftime:str):
        
        guild = interaction.guild
        err=None

        if self.ctfbot.require_role_cmd_name:
            is_admin = discord.utils.get(guild.roles, name=self.ctfbot.require_role_cmd_name)
            if not is_admin:
                await interaction.response.send_message(f'Required role ({self.ctfbot.require_role_cmd_name}) for creating CTF channel not found. Are you sure this role exists?', ephemeral=True)
                return
            
            can_run = False
            for role in interaction.user.roles:
                if self.ctfbot.require_role_cmd_name == role.name:
                    can_run = True
            if not can_run:
                await interaction.response.send_message(f'You do not have the required role ({self.ctfbot.require_role_cmd_name}) to create/manage a CTF.', ephemeral=True)
                return
            
        overwrites = None
        if self.ctfbot.require_role_name:
            active_ctf_role = discord.utils.get(guild.roles, name=self.ctfbot.require_role_name)
            if not active_ctf_role:
                await interaction.response.send_message(f'Required role ({self.ctfbot.require_role_name}) for CTF room not found. Are you sure this role exists?', ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                active_ctf_role: discord.PermissionOverwrite(view_channel=True)
            }

        category = discord.utils.get(guild.categories, name=ctf_name)
        if not category:
            await interaction.response.send_message(f"CTF '{ctf_name}' doesn't exists.")
            return
        
        information_channel = discord.utils.get(category.channels, name='ctf-informations')
        if not information_channel:
            information_channel = await guild.create_text_channel('ctf-informations', category=category, overwrites=overwrites)
        
        informations,err = await get_ctftime_informations(ctftime)
        if not informations:
            await interaction.response.send_message(f"CTF {ctf_name} couldn't be updated with ctftime informations | err = {err}")
            return
        
        await information_channel.send(informations)
        await interaction.response.send_message(f'CTF {ctf_name} has been updated with ctftime event!')

    async def delete_ctf(self, interaction: discord.Interaction, ctf_name: str):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=ctf_name)

        if not category:
            await interaction.response.send_message(f'CTF {ctf_name} not found.', ephemeral=True)
            return
        
        tasks = []
        for channel in category.channels:
            tasks.append(asyncio.create_task(channel.delete()))
        await asyncio.gather(*tasks)

        await category.delete()
        await interaction.response.send_message(f'CTF {ctf_name} has been deleted')

    async def join_ctf(self, interaction : discord.Interaction, ctf_name:str, password:str):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=ctf_name)

        if not category:
            await interaction.response.send_message(f'CTF {ctf_name} not found.', ephemeral=True)
            return
        
        if password != self.ctfbot.ctf_password:
            await interaction.response.send_message('Incorrect password.', ephemeral=True)
            return

        required_role = discord.utils.get(guild.roles, name=self.ctfbot.require_role_name)
        if not required_role:
            await interaction.response.send_message(f'CTF role ({self.ctfbot.require_role_name}) not found.', ephemeral=True)
            return
        
        if required_role in interaction.user.roles:
            await interaction.response.send_message('You already have the required role.', ephemeral=True)
            return
        
        bot_member = guild.me
        if not bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message('I do not have permission to manage roles.', ephemeral=True)
            return

        bot_top_role = bot_member.top_role
        if bot_top_role <= required_role:
            await interaction.response.send_message('I cannot assign the role because it is higher or equal to my highest role.', ephemeral=True)
            return

        try:
            await interaction.user.add_roles(required_role)
            await interaction.response.send_message(f'You have successfully joined {ctf_name} and have been given the role: {self.ctfbot.require_role_name}.', ephemeral=True)
        except discord.DiscordException as e:
            await interaction.response.send_message(f'Failed to add role: {e}', ephemeral=True)


    async def unregister(self, interaction: discord.Interaction):
        guild = interaction.guild

        if self.ctfbot.require_role_cmd_name:
            is_admin = discord.utils.get(guild.roles, name=self.ctfbot.require_role_cmd_name)
            if not is_admin:
                await interaction.response.send_message(f'Required role ({self.ctfbot.require_role_cmd_name}) for creating CTF not found. Are you sure this role exists?', ephemeral=True)
                return
            
            can_run = False
            for role in interaction.user.roles:
                if self.ctfbot.require_role_cmd_name == role.name:
                    can_run = True
            if not can_run:
                await interaction.response.send_message(f'You do not have the required role ({self.ctfbot.require_role_cmd_name}) to create a CTF.', ephemeral=True)
                return
            
        required_role = discord.utils.get(guild.roles, name=self.ctfbot.require_role_name)
        if not required_role:
            await interaction.response.send_message(f'CTF role ({self.ctfbot.require_role_name}) not found.', ephemeral=True)
            return

        if not guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message('I do not have permission to manage roles.', ephemeral=True)
            return

        bot_top_role = guild.me.top_role
        if bot_top_role <= required_role:
            await interaction.response.send_message('I cannot remove the role because it is higher or equal to my highest role.', ephemeral=True)
            return

        members_with_role = [member for member in guild.members if required_role in member.roles]

        for member in members_with_role:
            try:
                await member.remove_roles(required_role)
            except discord.DiscordException as e:
                await interaction.followup.send(f'Failed to remove role from {member.display_name}: {e}', ephemeral=True)

        await interaction.response.send_message(f'The role {self.ctfbot.require_role_name} has been removed from all users.', ephemeral=True)