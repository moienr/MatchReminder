import requests
#prety print
import pprint
import json

# Thanks to : https://www.football-data.org/
# Documentation : https://www.football-data.org/documentation/quickstart

# read token from file
with open('token.txt', 'r') as f:
	token = f.read()

url = "https://api.football-data.org/v4/teams/86/matches?status=SCHEDULED"
headers = {"X-Auth-Token": token}

response = requests.get(url, headers=headers)

if response.status_code == 200:
	# The request was successful
	matches = response.json()
	# Do something with the matches data
	pprint.pprint(matches)
	# save json
	with open('matches.json', 'w') as f:
		json.dump(matches, f)
else:
	# The request failed
	print("Error:", response.status_code, response.text)
