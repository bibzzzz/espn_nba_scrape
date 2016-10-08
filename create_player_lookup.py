import pandas as pd
import requests
from bs4 import BeautifulSoup
import os


years = [2011, 2012, 2013, 2014, 2015, 2016] #specify past seasons to scrape results for

full_player_table = pd.DataFrame(columns = ['player', 'player_id'])

BASE_URL = 'http://www.espn.com/nba/player/_/id/{0}'

for year in years:

    print 'loading boxscore data from %d season...' %(year)
    output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/' + str(year) + '/'
    #games_path = os.path.join(output_dir, 'errors.csv')
    players_path = os.path.join(output_dir, 'box_score_data.csv')

    #games = pd.read_csv(games_path, index_col=0)
    players = pd.read_csv(players_path, low_memory=False)
    players = players[['player', 'player_id']]
    full_player_table = pd.concat([full_player_table, players], axis=0, ignore_index=True)
    #full_player_table = pd.concat([full_player_table, players], axis=0, join='inner')
    #full_player_table = full_player_table.append(players, ignore_index=True)
    full_player_table.drop_duplicates(inplace=True)    #drop duplicate rows

player_full_names = pd.DataFrame(columns = ['player_id', 'player_full_name'])
for player_id in full_player_table['player_id']:
    r = requests.get(BASE_URL.format(int(player_id)))
    #soup = BeautifulSoup(r.text, "html.parser").find('div', class_='main-headshot')
    soup = BeautifulSoup(r.text, "html.parser").find('h1')
    #print soup.text
    #line = np.concatenate(([index, team_name], x)).reshape(1,len(columns))
    print soup.text
    #print np.concatenate(([player_id, soup.text]), 1).reshape(1,2)
    #new = pd.DataFrame(np.concatenate(player_id, soup.text).reshape(1,2), columns=player_full_names.columns)
    #frame = frame.append(new)
    player_full_names = player_full_names.append({'player_id':player_id, 'player_full_name':soup.text}, ignore_index=True)
    #print table.find_all('tr')[1:]

player_lookup_table = pd.merge(full_player_table, player_full_names, left_on='player_id', right_on='player_id')
player_lookup_table[['player_id']] = player_lookup_table[['player_id']].astype(int)

print 'storing player lookup table...'

output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'
lookup_output_filepath = os.path.join(output_dir, 'player_lookup_table.csv')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

player_lookup_table.to_csv(lookup_output_filepath, encoding = 'utf-8')
