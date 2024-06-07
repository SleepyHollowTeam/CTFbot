#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : ctfd_parser.py
# Author             : Podalirius (@podalirius_)
# Reused and modified by k4ndar3c

import argparse
import json
import requests
import re
import os
from concurrent.futures import ThreadPoolExecutor
import json
import shutil
import asyncio
from bs4 import BeautifulSoup as bs

ROOT = os.path.dirname(__file__)

FILE_MAX_SIZE_MO = 15 

def os_filename_sanitize(s:str) -> str:
    filtred = ['/', ';', ' ', ':']
    for char in filtred:
        s = s.replace(char, '_')
    s = re.sub('__*', '_', s)
    return s

class CTFdParser(object):

    def __init__(self:object, target:str, login:str,password:str,basedir:str="Challenges") -> None:
        super(CTFdParser, self).__init__()
        self.target = target
        self.basedir = basedir
        self.challenges = {}
        self.credentials = {
            'user': login,
            'password': password
        }
        self.session = requests.Session()
        
    def login(self:object) -> bool:
        r = self.session.get(self.target + '/login')
        matched = re.search(
            b"""('csrfNonce':[ \t]+"([a-f0-9A-F]+))""", r.content)
        nonce = ""
        if matched is not None:
            nonce = matched.groups()[1]
        r = self.session.post(
            self.target + '/login',
            data={
                'name': self.credentials['user'],
                'password': self.credentials['password'],
                '_submit': 'Submit',
                'nonce': nonce.decode('UTF-8')
            }
        )

        return 'Your username or password is incorrect' not in r.text

    async def get_challenges(self:object, threads:int=8) -> dict:
        r = self.session.get(self.target + "/api/v1/challenges")
        if r.status_code == 200:
            json_challs = json.loads(r.content)
            if json_challs is not None:
                if json_challs['success']:
                    self.challenges = json_challs['data']
                    all_challs = await self._parse()
                else:
                    print("[warn] An error occurred while requesting /api/v1/challenges")
            return json_challs, all_challs
        else:
            return None

    async def _parse(self:object):
        resp = []
        # Categories
        self.categories = [chall["category"] for chall in self.challenges]
        self.categories = sorted(list(set(self.categories)))

        print(f'\x1b[1m[\x1b[93m+\x1b[0m\x1b[1m]\x1b[0m Found {len(self.categories)} categories !')

        # Parsing challenges
        for category in self.categories:
            print(f"\x1b[1m[\x1b[93m>\x1b[0m\x1b[1m]\x1b[0m Parsing challenges of category : \x1b[95m{category}\x1b[0m")

            challs_of_category = [c for c in self.challenges if c['category'] == category]

            # Waits for all the threads to be completed
            #with ThreadPoolExecutor(max_workers=min(threads, len(challs_of_category))) as tp:
            for challenge in challs_of_category:
                chall, res, fname = await self.dump_challenge(category, challenge)
                resp.append((chall, res, fname))
        return resp

    async def dump_challenge(self:object, category:str, challenge:dict):
        if challenge["solved_by_me"]:
            print(f"   \x1b[1m[\x1b[93m>\x1b[0m\x1b[1m]\x1b[0m \x1b[1;92m✅\x1b[0m \x1b[96m{challenge['name']}\x1b[0m")
        else:
            print(f"   \x1b[1m[\x1b[93m>\x1b[0m\x1b[1m]\x1b[0m \x1b[1;91m❌\x1b[0m \x1b[96m{challenge['name']}\x1b[0m")

        folder = os.path.sep.join([self.basedir, os_filename_sanitize(category), os_filename_sanitize(challenge["name"])])
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        try:
            # Readme.md
            res = ""
            fname = False
            f = open(folder + os.path.sep + "README.md", 'w')
            f.write(f"# {challenge['name']}\n\n")
            f.write(f"**Category** : {challenge['category']}\n")
            f.write(f"**Points** : {challenge['value']}\n\n")
            
            res += f"# {challenge['name']}\n\n"
            res += f"**Category** : {challenge['category']}\n"
            res += f"**Points** : {challenge['value']}\n\n"

            chall_json = self.get_challenge_by_id(challenge["id"])["data"]
            description = bs(chall_json['description'], 'html.parser').get_text(separator="\n")
            f.write(f"{description}\n\n")
            res += f"{description}\n\n"

            connection_info = chall_json["connection_info"]
            if connection_info is not None:
                if len(connection_info) != 0:
                    f.write(f"{connection_info}\n\n")
                    res += f"{connection_info}\n\n"

            # Get challenge files
            if len(chall_json["files"]) != 0:
                f.write("## Files : \n")
                for file_url in chall_json["files"]:
                    if "?" in file_url:
                        filename = os.path.basename(file_url.split('?')[0])
                    else:
                        filename = os.path.basename(file_url)

                    r = self.session.head(self.target + file_url, allow_redirects=True)
                    if "Content-Length" in r.headers.keys():
                        size = int(r.headers["Content-Length"])
                        if size < (FILE_MAX_SIZE_MO * 1024 * 1024):  # 50 Mb
                            r = self.session.get(self.target + file_url, stream=True)
                            fname = folder + os.path.sep + filename
                            with open(folder + os.path.sep + filename, "wb") as fdl:
                                for chunk in r.iter_content(chunk_size=16 * 1024):
                                    fdl.write(chunk)
                        else:
                            print(f"Not Downloading {filename}, filesize too big.")

                    else:
                        r = self.session.get(self.target + file_url, stream=True)
                        with open(folder + os.path.sep + filename, "wb") as fdl:
                            for chunk in r.iter_content(chunk_size=16 * 1024):
                                fdl.write(chunk)

                    f.write(f" - [{filename}](./{filename})\n")

            f.write("\n\n")
            f.close()
            return challenge['name'], res, fname
        except Exception as e:
            print(e)
            f.close()
            return challenge['name'], res, fname

    def get_challenge_by_id(self:object, chall_id:int) -> dict:
        """Documentation for get_challenge_by_id"""
        r = self.session.get(self.target + f'/api/v1/challenges/{chall_id}')
        json_chall = None
        if r.status_code == 200:
            json_chall = json.loads(r.content)
        return json_chall


async def dump_ctfd(ctf_url, user, password):
    if not ctf_url.startswith("http://") and not ctf_url.startswith("https://"):
        ctf_url = "https://" + ctf_url
    output = ctf_url.split("//")[1]
    
    cp = CTFdParser(ctf_url, user, password, output)
    if cp.login():
        challs, all_challs = await cp.get_challenges()
        return challs, all_challs
    else:
        return False, False
    



