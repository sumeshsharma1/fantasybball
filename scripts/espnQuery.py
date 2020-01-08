def espn_fantasy_pull(year, leagueid):
    import requests
    import csv
    from datetime import datetime, timedelta
    import locale
    locale.setlocale( locale.LC_ALL, '' )
    currentdate = datetime.now()
    futuredate = currentdate + timedelta(days=7)

    url = "https://fantasy.espn.com/apis/v3/games/fba/seasons/" + str(year) + "/segments/0/leagues/" + str(leagueid)

    teamdata = requests.get(url).json()
    matchups = requests.get(url, params={"view": "mMatchup"}).json()

    teamMap = {}

    for team in teamdata['teams']:
        teamMap[team['id']] = team['location'] + " " + team['nickname']

    player_list = []

    for j in range(len(matchups['teams'])):
        for i in range(len(matchups['teams'][j]['roster']['entries'])):
            player = matchups['teams'][j]['roster']['entries'][i]['playerPoolEntry']['player']['fullName']
            if player[-3:] in ['Jr.', 'Sr.', 'III']:
                player = player[:-4]
            elif player[-3:] == " II":
                player = player[:-3]
            else:
                player = player
            player = player.replace(".","")
            player_list.append(player)
    return player_list

# espn_team_pull returns a dictionary of each team in the league as keys and a list of
# players in that league as the values. 
def espn_team_pull(year, leagueid):
    import requests
    import csv
    from datetime import datetime, timedelta
    import locale
    locale.setlocale( locale.LC_ALL, '' )
    currentdate = datetime.now()
    futuredate = currentdate + timedelta(days=7)

    url = "https://fantasy.espn.com/apis/v3/games/fba/seasons/" + str(year) + "/segments/0/leagues/" + str(leagueid)

    teamdata = requests.get(url).json()
    matchups = requests.get(url, params={"view": "mMatchup"}).json()

    teamMap = {}

    for team in teamdata['teams']:
        teamMap[team['id']] = team['location'] + " " + team['nickname']



    fullMap = {}

    for j in range(len(matchups['teams'])):
        player_list = []
        for i in range(len(matchups['teams'][j]['roster']['entries'])):
            player = matchups['teams'][j]['roster']['entries'][i]['playerPoolEntry']['player']['fullName']
            if player[-3:] in ['Jr.', 'Sr.', 'III']:
                player = player[:-4]
            elif player[-3:] == " II":
                player = player[:-3]
            else:
                player = player
            player = player.replace(".","")
            player_list.append(player)
        fullMap[teamMap[j+1]] = player_list

    return fullMap
