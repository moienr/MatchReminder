import requests
#prety print
import pprint
import json

# Thanks to : https://www.football-data.org/
# Documentation : https://www.football-data.org/documentation/quickstart

# read token from file
with open('token_api.txt', 'r') as f:
	token = f.read()

url = "https://api.football-data.org/v4/teams/81/matches?status=SCHEDULED"
headers = {"X-Auth-Token": token}

response = requests.get(url, headers=headers)

if response.status_code == 200:
	# The request was successful
	matches = response.json()
	# Do something with the matches data
	# pprint.pprint(matches)
	# save json
	with open('matches.json', 'w') as f:
		json.dump(matches, f, indent=4)
else:
	# The request failed
	print("Error:", response.status_code, response.text)



from datetime import datetime

def get_next_match(data, team_name):
   now = datetime.now()
   next_match = None

   for match in data['matches']:
       if match['homeTeam']['name'] == team_name or match['awayTeam']['name'] == team_name:
           match_date = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
           if match_date > now:
               if next_match is None or match_date < next_match['date']:
                  next_match = {
                      'date': match_date,
                      'match': match
                  }

   return next_match

def format_match(match):
   home_team = match['match']['homeTeam']['name']
   away_team = match['match']['awayTeam']['name']
   competition = match['match']['competition']['name']
   match_date = match['date'].strftime('%Y-%m-%d %H:%M:%S')

   return f'{home_team}-{away_team} | {competition} | @ {match_date}'


next_match = get_next_match(matches, 'FC Barcelona')
if next_match is not None:
   print(format_match(next_match))
else:
   print('No upcoming matches found for FC Barcelona.')
