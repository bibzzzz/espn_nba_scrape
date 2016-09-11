#import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, date

years = [2011, 2012, 2013, 2014, 2015, 2016] #specify past seasons to scrape results for
output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'
teams_path = os.path.join(output_dir, 'team_data.csv')

teams = pd.read_csv(teams_path, index_col=0)
BASE_URL = 'http://espn.go.com/nba/team/schedule/_/name/{0}/year/{1}/seasontype/2'
BASE_GAME_URL = 'http://espn.go.com/nba/boxscore?gameId={0}'

#LOOP THROUGH ALL SEASONS
for year in years:

    print 'scraping output from %d season...' %(year)

    game_id = []
    dates = []
    home_team = []
    home_team_score = []
    visit_team = []
    visit_team_score = []
    for index, row in teams.iterrows():
    # for index, row in teams[:1].iterrows():
        _team = index
        print(_team)
        r = requests.get(BASE_URL.format(row['prefix_1'], year))
        table = BeautifulSoup(r.text, "html.parser").table
        for row in table.find_all('tr')[1:]:
        # for row in table.find_all('tr')[1:3]:
            columns = row.find_all('td')

            try:
                _id = columns[2].a['href'].split('recap/_/id/')[1]
                _home = True if columns[1].li.text == 'vs' else False
                _other_team = columns[1].find_all('a')[1]['href']
                _other_team = _other_team.split('/')[-1:][0]
                _other_team = teams.index[teams['prefix_2'] == _other_team]
                _other_team = _other_team.values[0]
                _score = columns[2].a.text.split(' ')[0].split('-')
                _won = True if columns[2].span.text == 'W' else False

                game_id.append(_id)
                home_team.append(_team if _home else _other_team)
                visit_team.append(_team if not _home else _other_team)
                d = datetime.strptime(str(year) + ' ' + columns[0].text, '%Y %a, %b %d') #str(year) required due to issues with 29 Feb dates...
                dates.append(date(d.year, d.month, d.day))

                if _home:
                    if _won:
                        home_team_score.append(_score[0])
                        visit_team_score.append(_score[1])
                    else:
                        home_team_score.append(_score[1])
                        visit_team_score.append(_score[0])
                else:
                    if _won:
                        home_team_score.append(_score[1])
                        visit_team_score.append(_score[0])
                    else:
                        home_team_score.append(_score[0])
                        visit_team_score.append(_score[1])

            except Exception as e:
                pass # Not all columns row are a game, is OK
                # print(e)

    dic = {'id': game_id, 'date': dates, 'home_team': home_team, 'visit_team': visit_team, 
            'home_team_score': home_team_score, 'visit_team_score': visit_team_score}

    games = pd.DataFrame(dic).drop_duplicates().set_index('id')
    print 'storing output from %d season...' %(year)

    output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/' + str(year)
    output_filepath = os.path.join(output_dir, 'schedule_data.csv')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    games.to_csv(output_filepath, encoding='utf-8')

