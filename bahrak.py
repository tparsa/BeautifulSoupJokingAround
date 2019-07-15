from bs4 import BeautifulSoup as bs
edges = {}
all_teams = []

def add_game(first_team, second_team, score, date):
    global edges
    global all_teams

    teams_name = [first_team.text.strip(), second_team.text.strip()]
    if(teams_name[0] not in all_teams):
        all_teams.append(teams_name[0])
    if(teams_name[1] not in all_teams):
        all_teams.append(teams_name[1])
    score = score.text.strip()
    if(score[0] == '?'):
        return
    score = list(map(int, score.split(" - ")))
    if(score[0] > score[1]):
        if(teams_name[0] not in edges):
            edges[teams_name[0]] = []
        edges[teams_name[0]].append((teams_name[1], date))
    else:
        if(teams_name[1] not in edges):
            edges[teams_name[1]] = []
        edges[teams_name[1]].append((teams_name[0], date))

first_half = ["July", "August", "September", "October", "November", "December"]

def validate_games():
    for team in edges:
        for loser_team in edges[team]:
            if(not loser_team[1].split()[0] in first_half):
                continue
            cnt = 0
            for loser_team_iter in edges[team]:
                if(loser_team_iter[0] == loser_team[0] and loser_team_iter[1].split()[0] in first_half):
                    cnt += 1
            if(cnt > 1):
                return False
            if(loser_team[0] in edges):
                for loser_team_iter in edges[loser_team[0]]:
                    if(loser_team_iter[0] == team and loser_team_iter[1].split()[0] in first_half):
                        return False
    return True

def find_winners(team, all_teams):
    global edges
    winners = []
    for winner_team in edges:
        if(winner_team in all_teams):
            for team_date in edges[winner_team]:
                if(team_date[0] == team and team_date[1].split()[0] in first_half):
                    winners.append(winner_team)
                    break
    return winners

def find_losers(team, all_teams):
    global edges
    if(not team in edges):
        return []
    else:
        losers = []
        for loser_team in edges[team]:
            if(loser_team[0] in all_teams and loser_team[1].split()[0] in first_half):
                losers.append(loser_team[0])
        return losers

def find_hamiltonian_path(all_teams):
    global edges
    if(len(all_teams) == 1):
        return [all_teams[0]]
    for team in all_teams:
        if(team in edges):
            winners = find_winners(team, all_teams)
            losers = find_losers(team, all_teams)
            all_teams.remove(team)
            hamiltonian_path = []
            if(len(winners)):
                hamiltonian_path = find_hamiltonian_path(winners)
            hamiltonian_path.append(team)
            if(len(losers)):
                hamiltonian_path = hamiltonian_path + find_hamiltonian_path(losers)
            return hamiltonian_path

import requests
import lxml
import copy

response = requests.get('http://www.livescores.com/soccer/iran/persian-gulf-league/results/all')
print(response)

soup = bs(response.content, "lxml")
game_results = soup.find_all("div", "content")[0].find_all("div")

i = 0
for content in game_results:
    content_class = content.attrs['class']
    if(content_class[0] == "row" and content_class[2] == "bt0"):
        date = content.find_all("div", "tright")[0].text.strip()
    if(content_class[0] == "row-gray"):
        game_stat = content.find_all("div", "min")
        if(game_stat[0].text.strip() == "Canc." or game_stat[0].text.strip()[0].isdigit()):
            continue
        teams = content.find_all("div", "ply")
        score = content.find_all("a", "scorelink")
        score_div = content.find_all("div", "sco")
        if(len(score)):
            add_game(teams[0], teams[1], score[0], date)
        else:
            add_game(teams[0], teams[1], score_div[0], date)

if(validate_games()):
    print("Games are valid")
else:
    print("Duplication in games")
print("all teams:", len(all_teams), "teams", all_teams)
hamiltonian_path = find_hamiltonian_path(all_teams)
print("hamiltonian path:", hamiltonian_path)