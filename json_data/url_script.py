import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import pprint
import subprocess

def get_stat_urls(base_urls, start_year, end_year, last_year):
    urls = []
    for base in base_urls:
        start_year_loop = start_year 
        end_year_loop = end_year
        urls.append(base)

        match = re.search(r"/(stats|playingtime)/", base)
        if not match:
            continue
        section = match.group(1)

        # Extract league name from the last part of the URL
        base_parts = base.rstrip('/').split('/')
        last_part = base_parts[-1]  # e.g., "La-Liga-Stats"
        league_part = last_part.replace("-Stats", "")

        while start_year_loop > last_year:
            start_year_loop -= 1
            end_year_loop -= 1
            # Construct the historical URL
            historical = f"{'/'.join(base_parts[:-2])}/{start_year_loop}-{end_year_loop}/{section}/{start_year_loop}-{end_year_loop}-{league_part}-Stats"
            urls.append(historical)
            print(historical)
    return urls

base_urls = [
    "https://fbref.com/en/comps/9/playingtime/Premier-League-Stats",
    "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "https://fbref.com/en/comps/12/playingtime/La-Liga-Stats",
    "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
    "https://fbref.com/en/comps/11/playingtime/Serie-A-Stats",
    "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "https://fbref.com/en/comps/20/playingtime/Bundesliga-Stats",
    "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
    "https://fbref.com/en/comps/13/playingtime/Ligue-1-Stats",
    "https://fbref.com/en/comps/13/stats/Ligue-1-Stats"
]

start_year = 2024
end_year = 2025
last_year = 1988

urls = get_stat_urls(base_urls, start_year, end_year, last_year)
