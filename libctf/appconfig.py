from os import makedirs
from pathlib import Path
import json

ctf_channels_default = ["crypto", "rev", "pwn", "web", "forensic", "misc"]

def register_new_channels():
    print("Please enter channel in the order you want like this : channel1,channel2,channel3")
    r = input(">")
    channels = r.split(",")

    print("Those channels will be created in the ctf")
    for chan in channels:
        print(f"-> {chan}")

    print("Is this okay? (Y/N)")
    r2 = input(">")
    match r2:
        case 'Y' | 'y':
            return channels
        case default:
            register_new_channels()

def add_new_appconfig(ressource_dir) -> dict:
        appconfig = {}
        makedirs(ressource_dir, exist_ok=True)
        print("No appconfig registered, need to register one")
        print("Will all users will be able to join CTF ? (Y/N)")
        r = input(">")
        match r:
            case 'Y' | 'y':
                pass
            case 'N' | 'n':
                print("Name the role required to join CTF room")
                appconfig['require_role_name'] = input(">")
                print("Enter password to join CTF")
                appconfig["ctf_password"] = input(">")
            case default:
                print("Invalid response, Restarting")
                add_new_appconfig(ressource_dir)

        print("Will all users will be able to use CTFBot admin command (/create_ctf, ...) ? (Y/N)")
        r = input(">")
        match r:
            case 'Y' | 'y':
                pass
            case 'N' | 'n':
                print("Name the role required to use CTFBot command")
                appconfig['require_role_cmd_name'] = input(">")
            case default:
                print("Invalid response, Restarting")
                add_new_appconfig(ressource_dir)

        print("Those channels will be created in the ctf")
        for chan in ctf_channels_default:
            print(f"-> {chan}")

        print("Would you like to modify ? (Y/N)")
        r = input(">")
        match r:
            case 'Y' | 'y':
                channels = register_new_channels()
                appconfig["ctf_channels"] = channels
            case 'N' | 'n':
                appconfig["ctf_channels"] = ctf_channels_default
            case default:
                print("Invalid response, Restarting")
                add_new_appconfig(ressource_dir)

        appconfig_path = Path(ressource_dir / "appconfig.json")
        with open(appconfig_path, "w") as fd:
            fd.write(json.dumps(appconfig, indent=4))

        return appconfig

def register_appconfig(ressource_dir : Path) -> dict:

    if not ressource_dir.exists():
        return add_new_appconfig(ressource_dir)

    appconfig_path = Path(ressource_dir / "appconfig.json")
    if not appconfig_path.exists():
        return add_new_appconfig(ressource_dir)

    with open(appconfig_path,"rb") as fd:
        return json.loads(fd.read())
