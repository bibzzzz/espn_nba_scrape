import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, date

#years = [2011, 2012, 2013, 2014, 2015, 2016] #specify past seasons to scrape results for
years = [2011]

def get_players(players, team_name):
    array = np.zeros((len(players), len(headers) + 3), dtype=object)
    array[:] = np.nan
    for i, player in enumerate(players):
        #print player
        cols = player.find_all('td')
        position_elem = cols[0].find('span', {'class': 'position'}) #want to seperate position attribute to avoid concatenation issue with player_name
        if not position_elem == None: #in ['TEAM', '']:
            position_elem.replace_with('')
            player_id = cols[0].a['href'].split('_/id/')[1]
            #player_name = cols[0].text.split(',')[0]
            player_name = cols[0].find('span', {'class': 'abbr'})
            #print cols[0]
            #print player_name.text
    #        array[i, 0] = cols[0].text.split(',')[0]
            array[i, 0] = player_name.text
            array[i, 1] = int(player_id)
            array[i, 2] = position_elem.text

    #        print cols[0].text.split(',')[0]
            for j in range(1, len(headers) + 1):
                if not cols[1].text.startswith(('DNP', 'Did not play')):
                    #print cols[j].text
                    array[i, j + 2] = cols[j].text

    frame = pd.DataFrame(columns=columns)
    for x in array:
        line = np.concatenate(([index, team_name], x)).reshape(1,len(columns))
        new = pd.DataFrame(line, columns=frame.columns)
        frame = frame.append(new)
    return frame

for year in years:

    print 'scraping boxscore data from %d season...' %(year)
    output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/' + str(year) + '/'
    games_path = os.path.join(output_dir, 'schedule_data.csv')

    games = pd.read_csv(games_path, index_col=0)
    n_games = len(games)

    BASE_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'
    request = requests.get(BASE_URL.format(games.index[0]))

    table = BeautifulSoup(request.text, "html.parser").find('table', class_='mod-data')
    heads = table.find_all('thead')
    headers = heads[0].find_all('tr')[0].find_all('th')[1:]
    headers = [th.text for th in headers]
    columns = ['id', 'team', 'player', 'player_id', 'position'] + headers

    players = pd.DataFrame(columns = columns)
    error_list = pd.DataFrame(columns = ['game_id', 'home_team', 'visit_team'])

    game_no = 1
    #for index, row in games[:3].iterrows():
    for index, row in games.iterrows():
        #index = 400278191
        #print(index)

        try:
            request = requests.get(BASE_URL.format(index))
            table = BeautifulSoup(request.text, "html.parser").find('table', class_='mod-data')
            heads = table.find_all('thead')
            bodies = BeautifulSoup(request.text, "html.parser").find_all('tbody')[1:5]
            #bodies = table.find_all('tbody')

            team_1 = str(row.visit_team)
            team_1_players = bodies[0].find_all('tr') + bodies[1].find_all('tr')
            team_1_players = get_players(team_1_players, team_1)

            team_2 = str(row.home_team)
            team_2_players = bodies[2].find_all('tr') + bodies[3].find_all('tr')
            team_2_players = get_players(team_2_players, team_2)

            #append player box score data
            players = players.append(team_1_players)
            players = players.append(team_2_players)

            #raise Exception('manual test exception')

            print 'game %d stored! %d of %d complete' %(index, game_no, n_games)

        except Exception as e: #some links are broken... may need to update manually
            line = np.array([str(index), str(row.home_team), str(row.visit_team)]).reshape(1,len(error_list.columns))
            new = pd.DataFrame(line, columns = error_list.columns)
            error_list = error_list.append(new)
            print 'errored on game_id %d!' %(index)
            print str(e)

        game_no += 1

    players = players[pd.isnull(players.player) == False].set_index('id')
    error_list = error_list.set_index('game_id')
    print 'storing boxscore output from %d season...' %(year)

    #output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/' + str(year)
    player_output_filepath = os.path.join(output_dir, 'box_score_data.csv')
    error_output_filepath = os.path.join(output_dir, 'errors.csv')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    players.to_csv(player_output_filepath, encoding = 'utf-8')
    error_list.to_csv(error_output_filepath, encoding = 'utf-8')
