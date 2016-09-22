#import copper
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, date
#copper.project.path = '../../'

year = 2017
#teams = copper.read_csv('teams.csv')
output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'
teams_path = os.path.join(output_dir, 'team_data.csv')

teams = pd.read_csv(teams_path, index_col=0)
BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/seasontype/2'
BASE_GAME_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'

#print teams.index
#print teams.columns


dates = []
home_team = []
other_team = []
team = []
for index, row in teams.iterrows():
# for index, row in teams[:1].iterrows():
    _team = index
    print(_team)
    r = requests.get(BASE_URL.format(row['prefix_1'], year))
    table = BeautifulSoup(r.text, "html.parser").table
#    print table
    for row in table.find_all('tr')[1:]:
    # for row in table.find_all('tr')[1:3]:
        columns = row.find_all('td')
        #print columns
        #print columns[1]
        #print columns[2]

        try:
            #_id = columns[2].a['href'].split('recap/_/id/')[1]
            #print _id
            _home = True if columns[1].li.text == 'vs' else False
            #print _home
            _other_team = columns[1].find_all('a')[1]['href']
            _other_team = _other_team.split('/')[-1:][0]
            _other_team = teams.index[teams['prefix_2'] == _other_team]
            _other_team = _other_team.values[0]
            #print _other_team
#            _score = columns[2].a.text.split(' ')[0].split('-')
#            _won = True if columns[2].span.text == 'W' else False

            #game_id.append(_id)
            team.append(_team)
            home_team.append(1 if _home else 0)
            #print home_team
            other_team.append(_other_team)
            #print visit_team
            d = datetime.strptime(columns[0].text, '%a, %b %d')
            print d
            dates.append(date(year, d.month, d.day))

            # r = requests.get(BASE_GAME_URL.format(_id))
            # table = BeautifulSoup(r.text).find('table', class_='mod-data')
            # heads = table.find_all('thead')
            # bodies = table.find_all('tbody')
            # # print(heads)
            # headers = heads[2].tr.find_all('th')[2:]
            # headers = [th.text for th in headers]
            # headers[3] = headers[3].split('\n')[0]
            # del headers[-2]
            # visit_stats = bodies[2].tr.find_all('td')[1:]
            # visit_stats = [td.text for td in visit_stats]
            # del visit_stats[-2]
            # print(headers)
            # print(visit_stats)

        except Exception as e:
            pass # Not all columns row are a game, is OK
            # print(e)

#print len(team), len(home_team), len(other_team), len(dates)

dic = {'date': dates, 'opp_team': other_team, 'home_status': home_team}
games = pd.DataFrame(dic, index=team)
games.index.name = 'team'
#games = pd.DataFrame(dic).drop_duplicates().set_index('id')
#print(games)
#copper.save(games, 'games.csv')
output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/' + str(year)
output_filepath = os.path.join(output_dir, 'schedule_data.csv')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

games.to_csv(output_filepath, encoding='utf-8')

