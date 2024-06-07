# CtfBot

A ctfnote like discord bot to manage CTF  
Register mutiples command in discord to manage a CTF, can connect to ctftime and ctfd for better organisation!

## Installation

```bash
git clone X
cd ctfbot
pip3 install -r requirements.txt
pip3 install .
```

On discord develloper portal in bot section, be sure to add `Privileged Gateway Intents` (All Three) !
You will need a token. (via the develloper portal)

For config, you can use built in app config generation at first runtime or copy `template-appconfig.json` into `appconfig.json` in ressources folder

Be sure to put CTFBot role At the top ! (Or you can have permission error for assiging ctf role for example)

## Config example

In ressource/template-appconfig.json: 
```json
{
    "require_role_name" : "ActiveCTF",
    "require_role_cmd_name" : "Administrator",
    "ctf_channels" : ["rev","pwn","crypto","web","forensic","misc","hardware","web3","osint","mobile","radio","other"],
    "ctfpassword" : "dummypassword"
}
```

- require_role_name : Name of the role given to users that will join the CTF. Removing this from config will allow all users to join a ctf.
- require_role_cmd_name : Name of the role given to users that can use admin CTFBot commands such as `/create_ctf`, `/delete_ctf`, etc . Removing this from config will allow all users to use admin commands.
- ctf_channels : if no ctfd url + auth given, will use this list of channels when creating category and channels (+ctf-information if ctftime event url is given)
- ctfpassword : Password for command /join_ctf. This config is useless if `require_role_name` isn't present in config.

## Admin commands : 

- /create_ctf [CTFNAME] + Optional : [CTFTIME_EVENT_URL]
    * will create a list of channels based on ctf_channels in appconfig.json
    * if ctftime event url is given, will create ctf-information channel with ctftime information
- /get_ctfd [CTF_URL] [LOGIN] [PASS] [optional:UPDATE]: downloads the description and files for all categories of an online ctfd
- /delete_ctf [CTFNAME] : Delete the category [CTFNAME] and all of the channels
- /unregister : Remove `require_role_name` from all users
- /link_ctftime [CTFNAME] [CTFTIME_EVENT_URL] : Update or add ctftime information to ctf-information channel

## user commands : 

- /join_ctf [CTFNAME] [PASSWORD] : Give the user `require_role_name`, allowing to see private ctf category and channels

This command is useless when `require_role_name` is not present in config

## usage

Run 
```
python3 ctfbot.py
```

OR 

```
python3 -m ctfbot
```

## TODO

- appconfig:maxctfd_weight_upload
- bettername for `require_role_name`, `require_role_cmd_name`
- ctfd full feature
