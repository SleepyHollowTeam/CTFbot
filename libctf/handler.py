import discord
from discord import app_commands
from discord.ext import commands
import asyncio, json

import logging
logging.basicConfig(level=logging.DEBUG)

from .ctftime import get_ctftime_informations
from .ctfd_parser import dump_ctfd
from .selenium_firefox import take_screenshot
from .utils import *

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

        @self.ctfclient.tree.command(
            name="get_ctfd",
            description="Get an online CTFd and create category for it"
        )
        @app_commands.describe(ctf_url="The url of the CTFd",
                               user="login",
                               password="password",
                               update="Optional: update new challs")
        async def get_ctfd(interaction: discord.Interaction, ctf_url: str, user: str, password: str, update: bool = False):
            await self.get_ctfd(interaction, ctf_url, user, password, update)

        @self.ctfclient.tree.command(
            name="next_ctfs",
            description="Get a list of incoming ctfs"
        )
        @app_commands.describe(quantity="Optional: How many (default 15)")
        async def next_ctfs(interaction: discord.Interaction, quantity:int = 15):
            await self.next_ctfs(interaction, quantity)

        @self.ctfclient.tree.command(
            name="clean",
            description="Delete last messages in channel"
        )
        @app_commands.describe(quantity="Optional: How many (default 15)")
        async def clean(interaction: discord.Interaction, quantity:int = 15):
            await self.clean(interaction, quantity)

        @self.ctfclient.tree.command(
            name="ping",
            description="Simple ping/pong"
        )
        @app_commands.describe()
        async def ping(interaction: discord.Interaction):
            await self.ping(interaction)

        @self.ctfclient.tree.command(
            name="get_score",
            description="Get a screenshot of a team's page"
        )
        @app_commands.describe(team_url="The url of the team")
        async def get_score(interaction: discord.Interaction, team_url: str):
            await self.get_score(interaction, team_url)

        @self.ctfclient.tree.command(
            name="infos",
            description="Show links about SH"
        )
        @app_commands.describe()
        async def infos(interaction: discord.Interaction):
            await self.infos(interaction)

        @self.ctfclient.tree.command(
            name="make_button",
            description="Create a button to auto join a ctf"
        )
        @app_commands.describe(name="CTF name")
        async def make_button(interaction: discord.Interaction, name: str):
            self.ctf_name = name
            await self.button_command(interaction)

    async def get_score(self, interaction: discord.Interaction, team_url: str):
        chan = interaction.channel
        if '/teams/' not in team_url.lower():
            interaction.response.send_message("Can't scrape the web :)")
        r = await take_screenshot(team_url)
        if r:
            await chan.send(file=discord.File("team_score.png"))
        else:
            await chan.send(f'[-] request "{team_url}" failed')

    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("I'm up !")

    async def button_command(self, interaction):
        view = ActivateButton(self.ctf_name, self.join_ctf)
        channel = discord.utils.get(interaction.guild.text_channels, name="planning-ctf")
        if channel is not None:
            await channel.send(f"**-> To join {self.ctf_name}**", view=view)

    async def infos(self, interaction: discord.Interaction):
        urls = ["https://ctftime.org/team/282180", "https://sleepyhollow.netlify.app/", "https://github.com/SleepyHollowTeam", "https://x.com/SleepyHollowCTF"]
        await interaction.response.send_message(f"<{urls[0]}>\n<{urls[1]}>\n<{urls[2]}>\n<{urls[3]}>")

    async def clean(self, interaction: discord.Interaction, quantity:int = 15):
        async for msg in interaction.channel.history(limit=quantity):
            await msg.delete()
            await asyncio.sleep(.5)

    async def next_ctfs(self, interaction: discord.Interaction, quantity:int = 15):
        await interaction.response.send_message("```{}```".format(get_next_ctfs(quantity)))


    async def get_ctfd(self, interaction: discord.Interaction, ctf_url: str, user: str, password: str, update: bool = False):

        guild = interaction.guild
        channel = interaction.channel

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

        if "//" in ctf_url:
            ctf_name = ctf_url.split("//")[1].rstrip('/')
        else:
            ctf_name = ctf_url.rstrip('/')
        category = discord.utils.get(guild.categories, name=ctf_name)

        if not category or update:

            challs, challs_data = await dump_ctfd(ctf_url, user, password)
            if not challs:
                await interaction.response.send_message(f"[-] Can't connect to {ctf_url} with login {user}/{password}")
                return
            challs = challs['data']
            cats = set([x['category'] for x in challs])

            if not update:
                category = await guild.create_category(ctf_name, overwrites=overwrites)

            for cat_name in cats:
                local_cat_name = "ctf-"+cat_name.lower().replace(' ', '-')
                try:
                    chan = discord.utils.get(guild.channels, name=local_cat_name)
                    if not chan:
                        chan = await guild.create_text_channel(local_cat_name, category=category, overwrites=overwrites)

                    names = set([x['name'] for x in challs if x['category'] == cat_name])
                    for n in names:
                        thread = discord.utils.get(chan.threads, name=f"**{n}**")
                        if not thread:
                            message = await chan.send(f"Thread **{n}**")
                            thread = await message.create_thread(name=f"**{n}**")
                            for data in challs_data:
                                if data[0] == n:
                                    await thread.send(data[1])
                                    if data[2]:
                                        await thread.send(file=discord.File(data[2]))
                except Exception as e:
                    print(e)

            await channel.send(f'ctf {ctf_name} fully download.')
        else:
            await channel.send(f'Category {ctf_name} already exists.')

        if not update:
            self.ctf_name = ctf_name
            await self.button_command(interaction)


    async def create_ctf(self, interaction: discord.Interaction, ctf_name: str, ctftime:str = None):

        self.ctf_name = ctf_name
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
            await interaction.response.send_message(f"CTF {ctf_name} already exists.")
            return

        category = await guild.create_category(ctf_name, overwrites=overwrites)
        await guild.create_voice_channel(f'General-CTF', category=category, overwrites=overwrites)

        if ctftime:
            informations,err = await get_ctftime_informations(ctftime)
            information_channel = await guild.create_text_channel("informations", category=category, overwrites=overwrites)
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

        await self.button_command(interaction)


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

        information_channel = discord.utils.get(category.channels, name='informations')
        if not information_channel:
            information_channel = await guild.create_text_channel('informations', category=category, overwrites=overwrites)

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


class ActivateButton(discord.ui.View):
    def __init__(self, args, func):
        self.name = args
        self.func = func
        super().__init__(timeout=172800)

    @discord.ui.button(label="Join ActiveCTF", style=discord.ButtonStyle.primary)
    async def execute_command(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.func(interaction, self.name, json.load(open('ressource/appconfig.json','r'))['ctf_password'])
        #await interaction.response.send_message(f'You have role ActiveCTF !', ephemeral=True)


