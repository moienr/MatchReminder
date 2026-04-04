import requests
import re
import json

# FotMob Integration for Copa del Rey and lineup data
# Team ID for Barcelona: 8634

FOTMOB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}


def _extract_next_data(html):
    """Extract __NEXT_DATA__ JSON from FotMob HTML page."""
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html
    )
    if match:
        return json.loads(match.group(1))
    return None


def _fetch_fotmob_page(path):
    """Fetch a FotMob page and return the embedded __NEXT_DATA__."""
    url = f"https://www.fotmob.com{path}"
    try:
        response = requests.get(url, headers=FOTMOB_HEADERS, timeout=15)
        if response.status_code == 200:
            return _extract_next_data(response.text)
    except Exception as e:
        print(f"FotMob fetch error: {e}")
    return None


def get_fotmob_team_data():
    """Get Barcelona's full team data from FotMob."""
    data = _fetch_fotmob_page("/teams/8634/overview/barcelona")
    if not data:
        return None
    try:
        return data['props']['pageProps']['fallback']['team-8634']
    except (KeyError, TypeError):
        return None


def get_fotmob_current_match():
    """Get Barcelona's current/next match info from FotMob."""
    team = get_fotmob_team_data()
    if not team:
        return None
    return team.get('overview', {}).get('nextMatch')


def get_match_lineup():
    """Get the lineup for the current/next Barcelona match."""
    team = get_fotmob_team_data()
    if not team:
        return "❌ Unable to fetch data from FotMob."

    overview = team.get('overview', {})
    next_match = overview.get('nextMatch')
    if not next_match:
        return "❌ No current match found."

    match_id = next_match.get('id')
    opponent = next_match.get('opponent', {}).get('name', 'Unknown')
    tournament = next_match.get('tournament', {}).get('name', 'Unknown')
    status = next_match.get('status', {})

    has_ongoing = overview.get('hasOngoingMatch', False)
    barca_lineup = overview.get('lastLineupStats')

    if not barca_lineup:
        return "❌ Lineup not available yet for this match."

    home = next_match.get('home', {})
    away = next_match.get('away', {})
    home_name = home.get('name', 'Home')
    away_name = away.get('name', 'Away')

    lineup_text = f"⚽ *LINEUPS*\n\n"
    lineup_text += f"*{home_name}* vs *{away_name}*\n"
    lineup_text += f"_{tournament}_"

    if status.get('ongoing'):
        score = status.get('scoreStr', '')
        live_time = status.get('liveTime', {}).get('short', '')
        lineup_text += f" | 🔴 LIVE {score} ({live_time})"
    elif status.get('finished'):
        score = status.get('scoreStr', '')
        lineup_text += f" | FT {score}"

    lineup_text += "\n\n"

    is_home = home.get('id') == 8634
    barca_emoji = "🏠" if is_home else "✈️"
    opp_emoji = "✈️" if is_home else "🏠"

    # Barcelona lineup (from lastLineupStats)
    formation = barca_lineup.get('formation', 'N/A')
    lineup_text += f"{barca_emoji} *Barcelona* ({formation})\n"
    lineup_text += f"{'─' * 25}\n"

    for player in barca_lineup.get('starters', []):
        name = player['name']
        number = player.get('shirtNumber', '?')
        captain = " ©" if player.get('isCaptain') else ""

        events = player.get('performance', {}).get('events', [])
        event_str = ""
        for event in events:
            t = event.get('type', '')
            if t == 'goal':
                event_str += " ⚽"
            elif t == 'assist':
                event_str += " 🅰️"
            elif t == 'yellowCard':
                event_str += " 🟨"
            elif t == 'redCard':
                event_str += " 🟥"

        lineup_text += f"{number}. {name}{captain}{event_str}\n"

    bench = barca_lineup.get('bench', [])
    if bench:
        lineup_text += f"\n_Bench:_\n"
        for player in bench:
            name = player['name']
            number = player.get('shirtNumber', '?')
            events = player.get('performance', {}).get('events', [])
            event_str = ""
            for event in events:
                t = event.get('type', '')
                if t == 'substitutedOn':
                    event_str += " ⬆️"
                elif t == 'goal':
                    event_str += " ⚽"
            lineup_text += f"{number}. {name}{event_str}\n"

    return lineup_text
