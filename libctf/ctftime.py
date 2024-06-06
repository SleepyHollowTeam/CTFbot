import requests
import re
from typing import Tuple

# Discord bot seem to be denied by ctftime
headers = {
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0'
}

async def get_ctftime_informations(ctftime_link:str) -> Tuple[str,str]:
    id = await get_event_id_from_url(ctftime_link)
    if not id:
        return None,"Invalid Url format"
    
    event_info = await get_event_info(id)
    if not event_info:
        return None,"Invalid/Unknow Event ID from ctftime url"
    
    return pretty_print_ctftime_event(event_info),None

async def get_event_id_from_url(url:str) -> str:
    match = re.match(r'^https?://ctftime.org/event/(\d+)/?$', url)
    if match:
        return match.group(1)
    else:
        return None

async def get_event_info(event_id:int) -> dict:
    api_url = f"https://ctftime.org/api/v1/events/{event_id}/"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch event information. Status code: {response.status_code}")
        return None

def pretty_print_ctftime_event(event_info:dict) -> str:

    prectfname = ""
    if event_info.get("title"):
        prectfname = f"({event_info['title']})"
    message = f"**CTF Information {prectfname}**\n\n"
    if event_info.get("organizers"):
        message += "**Organizers** : "
        message += ','.join(x['name'] for x in event_info["organizers"])
    if event_info.get("ctftime_url"):
        message += f"**CtfTime URL** : {event_info['ctftime_url']}\n"
    if event_info.get("weight"):
        message += f"**CTF Weight** : {event_info['weight']}\n"
    if event_info.get("start"):
        message += f"**Start** : {event_info['start']}\n"
    if event_info.get("finish"):
        message += f"**End** : {event_info['finish']}\n"
    if event_info.get("duration"):
        message += f"**Total Duration** : {event_info['duration']['days']} days | {event_info['duration']['hours']} hours\n"
    if event_info.get("description"):
        message += f"**Description** : {event_info['description']}\n"
    if event_info.get("prizes"):
        message += f"**Prizes** : {event_info['prizes']}\n"
    if event_info.get("format"):
        message += f"**Format** : {event_info['format']}\n"
    if event_info.get("url"):
        message += f"**CTF Url** : {event_info['url']}\n"
    if event_info.get("logo"):
        message += event_info["logo"]
    return message