import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, date

years = [2011, 2012, 2013, 2014, 2015, 2016, 2017] #specify past seasons to scrape results for
#years = [2011]

league_id = 113799  #102953

BASE_URL = 'http://games.espn.com/fba/tools/projections?leagueId={0}&seasonId={1}&startIndex={2}'

def store_proj(projections, playernames):
    array = np.zeros((len(playernames), len(headers) + 2), dtype=object)
    array[:] = np.nan
    #print array
    for i, player in enumerate(playernames):
        if player == 'Nene': #Nene is breaking my code with his single name...
            player_short_name = 'N. Hilario'
        else:
            player_short_name = player[0] + '. ' + player.split(' ')[1] #regex the name split
        #print player_short_name
#        array[i, 0] = cols[0].text.split(',')[0]
        array[i, 0] = player.replace('*', '')
        array[i, 1] = player_short_name.replace('*', '')

#        print cols[0].text.split(',')[0]
        for j in range(0, len(headers)):
            array[i, j + 2] = projections[i][j].text

    frame = pd.DataFrame(columns=columns)
    for x in array:
        line = np.array(x).reshape(1,len(columns))
        new = pd.DataFrame(line, columns=frame.columns)
        frame = frame.append(new)
    return frame

for year in years:

    print 'scraping projections from %d season...' %(year)

    request = requests.get(BASE_URL.format(league_id, year, 0))
    table = BeautifulSoup(request.text, "html.parser").find('table', class_='playerTableTable tableBody')
    heads = table.find_all('tr', class_='playerTableBgRowSubhead tableSubHead')
    #print heads
    headers = heads[0].find_all('td', class_='playertableStat')
    headers = [th.text.strip() for th in headers]
    columns = ['player', 'player_short_name'] + headers
    #print columns
    proj_table = pd.DataFrame(columns = columns)

    startIndex = 0
    while startIndex <= 500:
        #try:
        print BASE_URL.format(league_id, year, startIndex)
        request = requests.get(BASE_URL.format(league_id, year, startIndex))
        table = BeautifulSoup(request.text, "html.parser").find('table', class_='playerTableTable tableBody')
        table_entries = table.find_all('tr', class_='pncPlayerRow')
        table_entries = [th.find_all('td', class_='playertableStat') for th in table_entries]
        playernames = table.find_all('td', class_='playertablePlayerName')
        playernames = [th.text.split(',')[0] for th in playernames]
        #print table_entries
        #print playernames
        #print len(table_entries), len(playernames)
        new_entries = store_proj(table_entries, playernames)

        proj_table = proj_table.append(new_entries)

        #except Exception as e:
        #    print str(e)
        #    pass

        startIndex += 40

    proj_table = proj_table[proj_table.FGM != '--'].set_index('player')
    proj_table = proj_table.drop(['PTS'], axis=1).join(proj_table['PTS'].ix[:, 0:1])    #duplicated PTS column, only want to retain average
    print 'storing projections data from %d season...' %(year)

    output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/' + str(year)
    proj_output_filepath = os.path.join(output_dir, 'init_projections.csv')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    proj_table.to_csv(proj_output_filepath, encoding = 'utf-8')
