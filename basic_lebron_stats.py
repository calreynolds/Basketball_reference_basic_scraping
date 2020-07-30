
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import functools as fc
import re
import sys

import warnings
#sns.set(style="darkgrid")
#get_ipython().run_line_magic('matplotlib', 'inline')


from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4 import Comment


# # This does not work currently for:
# 
# - Rookies
# - Retired Players

# Relevant links:
# lebron page: https://www.basketball-reference.com/players/j/jamesle01.html
# fred vanvleet page (free-agent):https://www.basketball-reference.com/players/v/vanvlfr01.html
# rj barret (rookie): https://www.basketball-reference.com/players/b/barrerj01.html
# deron williams (retired with a contract going to this year): https://www.basketball-reference.com/players/w/willide01.html

currentYear = "2019-20"

thisdict = {
    'Atlanta Hawks': 'ATL',
    'Brooklyn Nets': 'BKN',
    'Boston Celtics': 'BOS',
    'Charlotte Hornets': 'CHA',
    'Chicago Bulls': 'CHI',
    'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL',
    'Denver Nuggets': 'DEN',
    'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW',
    'Houston Rockets': 'HOU',
    'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL',
    'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL',
    'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP',
    'New Jersey Nets': 'NJN',
    'New York Knicks': 'NYK',
    'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL',
    'Philadelphia 76ers': 'PHI',
    'Phoenix Suns': 'PHX',
    'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC',
    'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR',
    'Utah Jazz': 'UTA',
    'Washington Wizards': 'WAS'
}

url = sys.argv[1]
html = urlopen(url)
rookie = False
retired = False

soup = BeautifulSoup(html, 'html.parser')

labels = [['Season', 'Age', 'Team', 'League', 'Position', 'GP', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'Name']]
labels_df = pd.DataFrame(labels)
title = str(soup.title)[7:]
match = re.match(r'.* S', title).group(0)
match = match[:-2]

def preprocess_data(soup):
	webpage_links = soup.find_all('tr', {'id': re.compile(r'per.game.*')})

	list_rows = []
	labels = []
	for row in webpage_links:
	    cells = row.find_all('td')
	    years = row.find('a')
	    str_years = str(years)
	    str_cells = str(cells)
	    clean = re.compile('<.*?>')
	    clean2 = (re.sub(clean, '',str_cells))
	    clean3 = (re.sub(clean, '',str_years))
	    list_rows.append([clean3 +"," + clean2])


	df = pd.DataFrame(list_rows)


	df1 = df[0].str.split(',', expand=True)
	# This deals with null 3P% values
	df1[13] = (df1[13].str.strip()).replace('', '.000')

	return df1



# --------------------------------------- Salary Info --------------------------------------- #
# 

def return_current_year_contract(salary_info, rookie):

	if not rookie:
	    contractsoup = BeautifulSoup(salary_info[1], 'html.parser')
	else:
		contractsoup = BeautifulSoup(salary_info[0], 'html.parser')

	# ------------- current contract ------------- #
	rows = contractsoup.find_all('tr')
	cleaned_data = []
	for elem in rows:
	    newcells = elem.find_all('th')
	    newcells2 = elem.find_all('td')
	    newcells3 = [newcells + newcells2]
	    str_newcells3 = str(newcells3)
	    clean5 = re.compile('<.*?>')
	    clean4 = (re.sub(clean5, '',str_newcells3))
	    cleaned_data.append(clean4)

	contract_df = pd.DataFrame(cleaned_data)
	contract_df = contract_df[0].str.split(', ', expand=True)
	team_name = contract_df[0][1].strip('[[')
	d = {'Season': [contract_df[1][0]], 'Salary': [contract_df[1][1]], 'Team': team_name}
	contract_df1 = pd.DataFrame(d)

	return contract_df1

def return_previous_salaries(salary_info, contract_df1, retired):
	cumulative_salaries = BeautifulSoup(salary_info[0], 'html.parser')

	cells2 = cumulative_salaries.find_all('tr')

	cleaned_salary = []

	for elem in cells2:
	    newcells = elem.find_all('th')
	    newcells2 = elem.find_all('td')
	    newcells3 = [newcells + newcells2]
	    str_newcells3 = str(newcells3)
	    clean5 = re.compile('<.*?>')
	    clean4 = (re.sub(clean5, '',str_newcells3))
	    cleaned_salary.append(clean4)

	salary_df = pd.DataFrame(cleaned_salary)[0].str.split(', ', expand=True)

	salary_df = salary_df.drop([2], axis=1)
	salary_df[0] = salary_df[0].str.strip('[[')
	salary_df[3] = salary_df[3].str.strip(']]')
	salary_df = salary_df.rename(columns=salary_df.iloc[0].str.strip())
	if not retired:
	    salary_df = salary_df.append(contract_df1)
	salary_df['Salary'] = salary_df['Salary'].str.strip(']]')
	salary_df['Season'] = salary_df['Season'].str.strip(']]')
	salary_df = salary_df[salary_df.Salary != 'Salary']
	salary_df = salary_df[salary_df.Season != 'Career']
	salary_df = salary_df[salary_df.Season != 'Team']

	salary_df['Salary'] = salary_df['Salary'].replace('[\$,]', '', regex=True).astype(float)

	return salary_df


# --------------------------------------- Finally, Data! ---------------------------------------


def combine_salary_and_stats(df1, contract_df1, salary_df, rookie):

	data_frames = [labels_df, df1]
	df4 = pd.concat(data_frames)

	df5 = df4.rename(columns=df4.iloc[0].str.strip())

	df6 = df5[df5.MP != 'MP']

	df6['Age'] = (df6['Age'].str.strip('['))
	df6['PTS'] = (df6['PTS'].str.strip(']'))
	df6['AST'] = df6['AST'].astype(float)

	df7 = df6.astype(str)

	df8 = df7.apply(fc.partial(pd.to_numeric, errors='ignore'))

	if not rookie:
		salary_df1 = salary_df.replace({"Team": thisdict}) 

	df9 = df8[~df8.Team.str.contains("TOT")]

	df9.Team = df9.Team.str.strip()
	if not rookie:
		salary_df1.Team = salary_df1.Team.str.strip()

	if rookie:
	    val = df9.Team[0].strip()
	    for key, value in thisdict.items(): 
	         if val == value:
	             contract_df1['Team'] = val

	if rookie:
		df = pd.merge(df9, contract_df1, right_index=True, on=['Season', 'Team'])
	else:
		df = pd.merge(df9, salary_df1, on=['Season', 'Team'])


	names = [match] * (df.shape[0])
	df['Name'] = names

	return df


def return_stats_pipeline():
	comments = soup.find_all(string=lambda text: isinstance(text, Comment))

	salary_info = []
	for c in comments:
	    if "salary" in c.extract() or "contracts" in c.extract():
	        salary_info.append(c.extract())

	df_initial = preprocess_data(soup)

	rookie = False
	retired = False
	if currentYear in str(salary_info) and df_initial.shape[0] == 1:
	    rookie = True
	elif currentYear not in str(salary_info) or currentYear not in str(df_initial[0]):
	    retired = True
	    salary_info = salary_info[:1]

	curr_contract = None
	if rookie or not retired:
		curr_contract = return_current_year_contract(salary_info, rookie)

	previous_salaries = None
	if not rookie:
		previous_salaries = return_previous_salaries(salary_info, curr_contract, retired)

	polished_stats = combine_salary_and_stats(df_initial, curr_contract, previous_salaries, rookie)
	return polished_stats


def main():
	polished_stats = return_stats_pipeline()
	print(polished_stats)


main()

