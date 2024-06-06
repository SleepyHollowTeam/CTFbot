from pathlib import Path
import discord
from os import makedirs

from discord import app_commands

from .handler import Handler
from .appconfig import register_appconfig

ROOT = Path(__file__).parent.parent

class DiscordClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix='/', intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


class CTFBot():
    def __init__(self) -> None:
        self.ressource_dir = Path(ROOT / "ressource")
        self.appconfig = {}

        self.register_app_token()
        print("Token registered")
        self.appconfig = register_appconfig(self.ressource_dir)
        print("Appconfig registered")

    @property
    def require_role(self) -> bool:
        return self.appconfig.get("require_role", False)
    @property
    def require_role_name(self) -> str:
        return self.appconfig.get("require_role_name",None)
    @property
    def ctf_channels(self) -> list:
        return self.appconfig.get("ctf_channels",["base"])

    def register_app_token(self) -> None:
        def add_new_token():
            makedirs(self.ressource_dir, exist_ok=True)
            print("No discord bot token registered, need to register one (go to https://discord.com/developers/applications and create a bot)")
            token = input("> ")
            self.token = token

            app_token_path = Path(self.ressource_dir / ".discord-token")
            with open(app_token_path, "w") as fd:
                fd.write(self.token)

        if not self.ressource_dir.exists():
            add_new_token()
            return

        app_token_path = Path(self.ressource_dir / ".discord-token")
        if not app_token_path.exists():
            add_new_token()
            return

        with open(app_token_path,"r") as fd:
            self.token = fd.read()

    
    def start(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guilds = True
        client = DiscordClient(intents=intents)       
        self.handler = Handler(client, self)
        client.run(self.token)


def main():
    bot = CTFBot()
    bot.start()
    
if __name__ == '__main__':
    main()