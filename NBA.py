import requests
from bs4 import BeautifulSoup
import string
import re
import pandas


url = "https://www.basketball-reference.com/players/"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "lxml")

alphabets = string.ascii_lowercase

player_names = []
player_urls = []
master_list = []


for alphabet in alphabets:
    index_link = soup.find_all("a", attrs={"href": re.compile(f"/players/{alphabet}/")})
    letter = soup.find_all("a", attrs={"href": f"/players/{alphabet}/"})
    index_link.remove(letter[0])

    for player in index_link:
        active_player = player.find_all("strong")
        if active_player != []:
            active_player_name = active_player[0].text
            player_names.append(active_player_name)
            player_urls.append(player["href"])


for url in player_urls:
    response = requests.get(f"https://www.basketball-reference.com/{url}")
    html = response.text
    soup = BeautifulSoup(html, "lxml")

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


data_frame = pandas.DataFrame(master_list)
data_frame.index += 1
data_frame.to_csv("NBA Career Stats.csv")
