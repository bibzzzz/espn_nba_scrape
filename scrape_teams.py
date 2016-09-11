import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

url = 'http://espn.go.com/nba/teams'
r = requests.get(url)

soup = BeautifulSoup(r.text, "html.parser")
tables = soup.find_all('ul', class_='medium-logos')

teams = []
prefix_1 = []
prefix_2 = []
for table in tables:
    lis = table.find_all('li')
    for li in lis:
        info = li.h5.a
        teams.append(info.text)
        url = info['href']
        prefix_1.append(url.split('/')[-2])
        prefix_2.append(url.split('/')[-1])


dic = {'prefix_2': prefix_2, 'prefix_1': prefix_1}
teams = pd.DataFrame(dic, index=teams)
teams.index.name = 'name'

output_dir = os.path.dirname(os.path.realpath(__file__)) + '/data/'
output_filepath = os.path.join(output_dir, 'team_data.csv')

if not os.path.exists(output_dir):
    os.makedirs(output_filepath)

teams.to_csv(output_filepath, encoding='utf-8')
