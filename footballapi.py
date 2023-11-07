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
from datetime import datetime
from pytz import timezone

def get_next_match(data, team_name):
   now = datetime.now().strftime('%Y-%m-%d')
   next_match = None

   for match in data['matches']:
       if match['homeTeam']['name'] == team_name or match['awayTeam']['name'] == team_name:
           match_date = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
           if match_date.strftime('%Y-%m-%d') >= now:
               if next_match is None or match_date < next_match['date']:
                  next_match = {
                      'date': match_date,
                      'match': match
                  }

   return next_match




def convert_utc_to_city(utc_datetime, to_city='Asia/Tehran'):
      utc = timezone('UTC')
      tehran = timezone(to_city)
      utc_time = datetime.strptime(utc_datetime, '%Y-%m-%dT%H:%M:%SZ')
      utc_time = utc.localize(utc_time)
      tehran_time = utc_time.astimezone(tehran)
      return tehran_time.strftime('%H:%M')



def format_today_match(match):
   home_team = match['match']['homeTeam']['name']
   away_team = match['match']['awayTeam']['name']
   competition = match['match']['competition']['name']
   match_date = match['date'].strftime('%Y-%m-%d %H:%M:%S')
   match_date_teh = convert_utc_to_city(match['match']['utcDate'], to_city='Asia/Tehran') 
   match_date_vanc = convert_utc_to_city(match['match']['utcDate'], to_city='America/Vancouver')

   return f'{home_team}-{away_team} | {competition} | @ TEH: {match_date_teh} - VANC: {match_date_vanc}'

def format_next_match(match):
   home_team = match['match']['homeTeam']['name']
   away_team = match['match']['awayTeam']['name']
   competition = match['match']['competition']['name']
   match_date = match['date'].strftime('%Y-%m-%d %H:%M:%S')
   match_date_teh = convert_utc_to_city(match['match']['utcDate'], to_city='Asia/Tehran') 
   match_date_vanc = convert_utc_to_city(match['match']['utcDate'], to_city='America/Vancouver')
   date = match['date'].strftime('%Y-%m-%d')
   return f'{home_team}-{away_team} | {competition} | Date: {date} | @ TEH: {match_date_teh} - VANC: {match_date_vanc}'

def does_barca_play_today(json_file='matches.json'):
   # read json
   with open(json_file, 'r') as f:
      matches = json.load(f)
      
   today = datetime.now()
   next_match = get_next_match(matches, 'FC Barcelona')['date']
   print(f"Today is {today.strftime('%Y-%m-%d')} | Next match is {next_match.strftime('%Y-%m-%d')}")
   if today.strftime('%Y-%m-%d') == next_match.strftime('%Y-%m-%d'):
      print('FC Barcelona plays today!')
      return True
   else:
      return False
   



def get_next_barca_match(json_file='matches.json'):
   # read json
   with open(json_file, 'r') as f:
      matches = json.load(f)
   next_match = get_next_match(matches, 'FC Barcelona')
   if next_match is not None:
      print(format_next_match(next_match))
      return format_next_match(next_match)
   else:
      print('No upcoming matches found for FC Barcelona.')
      return None
   
def get_barca_today_match(json_file='matches.json'):
   # read json
   with open(json_file, 'r') as f:
      matches = json.load(f)
   next_match = get_next_match(matches, 'FC Barcelona')
   if does_barca_play_today(json_file):
      print(format_today_match(next_match))
      return format_today_match(next_match)
   else:
      print('No upcoming matches found for FC Barcelona Today.')
      return None

if __name__ == '__main__':
   does_barca_play_today()
   get_next_barca_match('matches.json')
   get_barca_today_match('matches.json')