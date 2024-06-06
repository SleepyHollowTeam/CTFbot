import requests
import re
from typing import Tuple

# Discord bot seem to be denied by ctftime
headers = {
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0'
}

def get_ctftime_informations(ctftime_link:str) -> Tuple[dict,str]:
    id = get_event_id_from_url(ctftime_link)
    if not id:
        return {},"Invalid Url format"
    
    event_info = get_event_info(id)
    if not event_info:
        return {},"Invalid/Unknow Event ID from ctftime url"
    return event_info,None

def get_event_id_from_url(url):
    match = re.match(r'^https?://ctftime.org/event/(\d+)/?$', url)
    if match:
        return match.group(1)
    else:
        return None

def get_event_info(event_id):
    api_url = f"https://ctftime.org/api/v1/events/{event_id}/"
    print(api_url)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        print(f"Failed to fetch event information. Status code: {response.status_code}")
        return None

