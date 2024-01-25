# Scraping Nba website for player statistics data

import requests
from bs4 import BeautifulSoup
import string
import re
import pandas
import time

BASE_URL = "https://www.basketball-reference.com/players/"


def get_player(url):
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, "lxml")

        alphabets = string.ascii_lowercase

        player_names = []
        player_urls = []

        for alphabet in alphabets:
            index_link = soup.find_all(
                "a", attrs={"href": re.compile(f"/players/{alphabet}/")}
            )
            letter = soup.find_all("a", attrs={"href": f"/players/{alphabet}/"})
            if index_link:
                index_link.remove(letter[0])

            for player in index_link:
                active_player = player.find_all("strong")
                if active_player != []:
                    active_player_name = active_player[0].text
                    player_names.append(active_player_name)
                    player_urls.append(player["href"])

        return player_names, player_urls
    else:
        print(f"Failed to fetch data from {url}")
        return [], []


def get_stats():
    player_names, player_urls = get_player()
    master_list = []
    for url in player_urls:
        response = requests.get(f"https://www.basketball-reference.com/{url}")
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "lxml")

            try:
                part1 = soup.find("div", class_="p1").text.split()
                games = part1[1]
                points = part1[3]
                rebounds = part1[5]
                assists = part1[7]

                part2 = soup.find("div", class_="p2").text.split()
                fgp = part2[1]
                fgp3 = part2[3]
                ftp = part2[5]
                efgp = part2[7]

                part3 = soup.find("div", class_="p3").text.split()
                per = part3[1]
                ws = part3[3]
            except AttributeError:
                print(f"Data not found in {url}\nSkipping...")
                continue

            data_dict = {
                "Name": player_names[player_urls.index(url)],
                "Games": games,
                "Points": points,
                "Rebounds": rebounds,
                "Assists": assists,
                "FieldGoal%": fgp,
                "3Pts-FieldGoal%": fgp3,
                "FreeThrow%": ftp,
                "EffectiveFieldGoal%": efgp,
                "PlayerEfficiencyRating": per,
                "WinShares": ws,
            }
            master_list.append(data_dict)
        else:
            print(f"Failed to fetch data from {url}")

        delay = 2.5
        time.sleep(delay)

    return master_list


def create_excel():
    master_list = get_stats()
    data_frame = pandas.DataFrame(master_list)
    data_frame.index += 1
    try:
        data_frame.to_csv("NBA Career Stats.csv")
        print("Csv has been saved")
    except Exception as e:
        print(f"Failed to save Csv : {e}")

    count = len(master_list)
    print(
        f"The process has been completed.\nData of {count} players collected".center(20)
    )


get_player(BASE_URL)
get_stats()
create_excel()
