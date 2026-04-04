import requests
import pprint
import json
import io
from PIL import Image, ImageDraw, ImageFont

# Thanks to : https://www.football-data.org/
# Documentation : https://www.football-data.org/documentation/quickstart

# read token from file
with open('token_api.txt', 'r') as f:
	token = f.read()

url = "https://api.football-data.org/v4/teams/81/matches"
headers = {"X-Auth-Token": token}

response = requests.get(url, headers=headers)

if response.status_code == 200:
	# The request was successful
	matches_data = response.json()
	
	from datetime import datetime
	future_matches = [m for m in matches_data['matches'] 
	                  if datetime.strptime(m['utcDate'], '%Y-%m-%dT%H:%M:%SZ') > datetime.now()
	                  and m['status'] in ['SCHEDULED', 'TIMED', 'IN_PLAY']]
	
	# Sort by date
	future_matches.sort(key=lambda x: x['utcDate'])
	
	matches = {
		'filters': matches_data.get('filters', {}),
		'matches': future_matches
	}
	
	# save json
	with open('matches.json', 'w') as f:
		json.dump(matches, f, indent=4)
	print(f"Updated matches.json with {len(future_matches)} upcoming matches")
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
    city_tz = timezone(to_city)
    utc_time = datetime.strptime(utc_datetime, '%Y-%m-%dT%H:%M:%SZ')
    utc_time = utc.localize(utc_time)
    city_time = utc_time.astimezone(city_tz)
    return city_time.strftime('%H:%M')



def format_today_match(match):
    home_team = match['match']['homeTeam']['name']
    away_team = match['match']['awayTeam']['name']
    competition = match['match']['competition']['name']
    match_date_teh = convert_utc_to_city(match['match']['utcDate'], to_city='Asia/Tehran')
    match_date_vanc = convert_utc_to_city(match['match']['utcDate'], to_city='America/Vancouver')
    match_date_cet = convert_utc_to_city(match['match']['utcDate'], to_city='CET')
    
    if competition == 'Primera Division':
        competition = 'La Liga'

    return f'{home_team}-{away_team} | {competition} | @ TEH: {match_date_teh} - VANC: {match_date_vanc} - CET: {match_date_cet}'

def format_next_match(match):
    home_team = match['match']['homeTeam']['name']
    away_team = match['match']['awayTeam']['name']
    competition = match['match']['competition']['name']
    match_date_teh = convert_utc_to_city(match['match']['utcDate'], to_city='Asia/Tehran')
    match_date_vanc = convert_utc_to_city(match['match']['utcDate'], to_city='America/Vancouver')
    match_date_cet = convert_utc_to_city(match['match']['utcDate'], to_city='CET')
    days_left = (match['date'] - datetime.now()).days
    s = 's' if days_left > 1 else ''
    if competition == 'Primera Division':
        competition = 'La Liga'
    return f'{home_team}-{away_team} | {competition} | In {days_left} Day{s} | @ TEH: {match_date_teh} - VANC: {match_date_vanc} - CET: {match_date_cet}'

def does_barca_play_today(json_file='matches.json'):
   # Check football-data.org matches
   with open(json_file, 'r') as f:
      matches = json.load(f)
      
   today = datetime.now()
   next_match_data = get_next_match(matches, 'FC Barcelona')
   if next_match_data:
      next_match = next_match_data['date']
      print(f"Today is {today.strftime('%Y-%m-%d')} | Next match is {next_match.strftime('%Y-%m-%d')}")
      if today.strftime('%Y-%m-%d') == next_match.strftime('%Y-%m-%d'):
         print('FC Barcelona plays today!')
         return True

   # Fallback: check FotMob for matches not in football-data.org (Copa del Rey etc.)
   try:
      from fotmob_utils import get_fotmob_current_match
      fotmob_match = get_fotmob_current_match()
      if fotmob_match:
         status = fotmob_match.get('status', {})
         utc_time = status.get('utcTime', '')
         if utc_time:
            match_date = datetime.strptime(utc_time[:10], '%Y-%m-%d')
            if today.strftime('%Y-%m-%d') == match_date.strftime('%Y-%m-%d'):
               print('FC Barcelona plays today! (via FotMob)')
               return True
   except Exception as e:
      print(f"FotMob fallback error: {e}")

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
   if not does_barca_play_today(json_file):
      print('No upcoming matches found for FC Barcelona Today.')
      return None

   # Try football-data.org first
   with open(json_file, 'r') as f:
      matches = json.load(f)
   next_match = get_next_match(matches, 'FC Barcelona')
   today = datetime.now()

   if next_match and today.strftime('%Y-%m-%d') == next_match['date'].strftime('%Y-%m-%d'):
      print(format_today_match(next_match))
      return format_today_match(next_match)

   # Fallback: format from FotMob
   try:
      from fotmob_utils import get_fotmob_current_match
      fotmob_match = get_fotmob_current_match()
      if fotmob_match:
         home = fotmob_match.get('home', {}).get('name', '?')
         away = fotmob_match.get('away', {}).get('name', '?')
         tournament = fotmob_match.get('tournament', {}).get('name', '?')
         utc_time = fotmob_match.get('status', {}).get('utcTime', '')
         if utc_time:
            utc_date = utc_time.replace('.000Z', 'Z')
            match_date_teh = convert_utc_to_city(utc_date, to_city='Asia/Tehran')
            match_date_vanc = convert_utc_to_city(utc_date, to_city='America/Vancouver')
            match_date_cet = convert_utc_to_city(utc_date, to_city='CET')
            return f'{home}-{away} | {tournament} | @ TEH: {match_date_teh} - VANC: {match_date_vanc} - CET: {match_date_cet}'
   except Exception as e:
      print(f"FotMob fallback error: {e}")

   return None

def get_laliga_table():
    """Get the current La Liga standings"""
    url = "https://api.football-data.org/v4/competitions/PD/standings"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        standings_data = response.json()
        standings = standings_data['standings'][0]['table']
        
        table_text = "🏆 La Liga Table\n\n```\n"
        
        for team in standings:  # Show all teams
            pos = team['position']
            name = team['team']['name']
            points = team['points']
            gd = team['goalDifference']
            played = team['playedGames']
            
            # Highlight Barcelona
            if name.startswith("FC Barcelona") or name.startswith("Barcelona"):
                table_text += f"🔵🔴 {pos}. {name}\n"
            else:
                table_text += f"{pos}. {name}\n"
            
            table_text += f"   Pts: {points} | Played: {played} | GD: {gd:+d}\n\n"
        
        table_text += "```"
        return table_text
    else:
        return f"Error fetching La Liga table: {response.status_code}"


def _draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)


def get_laliga_table_image():
    """Generate a graphic La Liga standings table. Returns (BytesIO, caption) or (None, error)."""
    url = "https://api.football-data.org/v4/competitions/PD/standings"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None, f"Error fetching La Liga table: {response.status_code}"

    standings_data = response.json()
    standings = standings_data['standings'][0]['table']

    ROW_H = 32
    HEADER_H = 60
    PAD = 16
    W = 620
    H = HEADER_H + len(standings) * ROW_H + PAD * 2

    bg = (25, 25, 30)
    header_bg = (40, 40, 50)
    row_even = (32, 32, 38)
    row_odd = (38, 38, 45)
    barca_bg = (20, 40, 70)
    text_color = (220, 220, 220)
    dim_text = (150, 150, 160)
    accent = (100, 140, 230)
    gold = (220, 190, 60)
    green = (60, 180, 80)
    red = (200, 60, 50)
    separator = (55, 55, 65)

    img = Image.new('RGB', (W, H), bg)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
        font_row = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_row_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    except:
        font_title = font_header = font_row = font_row_bold = ImageFont.load_default()

    # Title
    title = "La Liga Standings"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 12), title, fill=gold, font=font_title)

    # Column positions
    col_pos = 24
    col_name = 55
    col_p = 320
    col_w = 370
    col_d = 410
    col_l = 450
    col_gd = 490
    col_pts = 555

    # Header row
    hy = HEADER_H - 18
    draw.text((col_pos, hy), "#", fill=dim_text, font=font_header)
    draw.text((col_name, hy), "TEAM", fill=dim_text, font=font_header)
    draw.text((col_p, hy), "P", fill=dim_text, font=font_header)
    draw.text((col_w, hy), "W", fill=dim_text, font=font_header)
    draw.text((col_d, hy), "D", fill=dim_text, font=font_header)
    draw.text((col_l, hy), "L", fill=dim_text, font=font_header)
    draw.text((col_gd, hy), "GD", fill=dim_text, font=font_header)
    draw.text((col_pts, hy), "PTS", fill=dim_text, font=font_header)

    # Rows
    for i, team in enumerate(standings):
        y = HEADER_H + i * ROW_H
        pos = team['position']
        name = team['team']['name']
        played = team['playedGames']
        won = team['won']
        drawn = team['draw']
        lost = team['lost']
        gd = team['goalDifference']
        points = team['points']

        is_barca = name.startswith("FC Barcelona") or name.startswith("Barcelona")

        # Row background
        if is_barca:
            row_bg = barca_bg
        elif i % 2 == 0:
            row_bg = row_even
        else:
            row_bg = row_odd
        draw.rectangle([PAD, y, W - PAD, y + ROW_H], fill=row_bg)

        # UCL / relegation zone indicators
        if pos <= 4:
            draw.rectangle([PAD, y, PAD + 3, y + ROW_H], fill=green)
        elif pos >= 18:
            draw.rectangle([PAD, y, PAD + 3, y + ROW_H], fill=red)

        ry = y + 8
        row_font = font_row_bold if is_barca else font_row
        name_color = accent if is_barca else text_color

        # Truncate long names
        if len(name) > 28:
            name = name[:26] + ".."

        draw.text((col_pos, ry), str(pos), fill=dim_text, font=row_font)
        draw.text((col_name, ry), name, fill=name_color, font=row_font)
        draw.text((col_p, ry), str(played), fill=text_color, font=row_font)
        draw.text((col_w, ry), str(won), fill=text_color, font=row_font)
        draw.text((col_d, ry), str(drawn), fill=text_color, font=row_font)
        draw.text((col_l, ry), str(lost), fill=text_color, font=row_font)

        gd_color = green if gd > 0 else (red if gd < 0 else dim_text)
        draw.text((col_gd, ry), f"{gd:+d}", fill=gd_color, font=row_font)

        draw.text((col_pts, ry), str(points), fill=gold if is_barca else text_color, font=font_row_bold)

        # Separator line
        draw.line([(PAD, y + ROW_H), (W - PAD, y + ROW_H)], fill=separator, width=1)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf, "La Liga Standings"


def get_barca_latest_score():
    """Get the score of Barcelona's most recent or live match"""
    # Fetch finished and in-play matches
    url = "https://api.football-data.org/v4/teams/81/matches?status=FINISHED,IN_PLAY"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return f"Error fetching match data: {response.status_code}"
    
    matches_data = response.json()
    matches = matches_data.get('matches', [])
    
    if not matches:
        return "No recent matches found for FC Barcelona."
    
    # Get the most recent match (last in the list)
    latest_match = matches[-1]
    
    home_team = latest_match['homeTeam']['name']
    away_team = latest_match['awayTeam']['name']
    home_score = latest_match['score']['fullTime']['home']
    away_score = latest_match['score']['fullTime']['away']
    status = latest_match['status']
    competition = latest_match['competition']['name']
    match_date = datetime.strptime(latest_match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
    
    if competition == 'Primera Division':
        competition = 'La Liga'
    
    # Format the date
    date_str = match_date.strftime('%b %d, %Y')
    
    # Build the message based on match status
    if status == 'IN_PLAY':
        score_text = f"⚽ *LIVE MATCH*\n\n"
        score_text += f"{home_team} {home_score} - {away_score} {away_team}\n"
        score_text += f"{competition}\n"
    elif status == 'FINISHED':
        score_text = f"⚽ *Latest Result*\n\n"
        score_text += f"{home_team} {home_score} - {away_score} {away_team}\n"
        score_text += f"{competition} | {date_str}\n"
        
        # Add result indicator for Barcelona
        if home_team == 'FC Barcelona':
            if home_score > away_score:
                score_text += "\n🔵🔴 Barcelona Won! 🎉"
            elif home_score < away_score:
                score_text += "\n😔 Barcelona Lost"
            else:
                score_text += "\n🤝 Draw"
        else:
            if away_score > home_score:
                score_text += "\n🔵🔴 Barcelona Won! 🎉"
            elif away_score < home_score:
                score_text += "\n😔 Barcelona Lost"
            else:
                score_text += "\n🤝 Draw"
    else:
        score_text = f"Match status: {status}"
    
    return score_text


if __name__ == '__main__':
   does_barca_play_today()
   get_next_barca_match('matches.json')
   get_barca_today_match('matches.json')