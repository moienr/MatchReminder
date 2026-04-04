import requests
import re
import json
import io
from PIL import Image, ImageDraw, ImageFont

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


def _draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)


def _rating_color(rating):
    """Return color based on rating value."""
    if rating >= 8.0:
        return (30, 180, 60)
    elif rating >= 7.0:
        return (80, 170, 50)
    elif rating >= 6.5:
        return (200, 160, 30)
    elif rating >= 6.0:
        return (210, 120, 30)
    else:
        return (200, 60, 40)


def generate_lineup_image(lineup_data, match_info=None):
    """Generate a pitch lineup image from FotMob lineup data.
    
    Returns a BytesIO object containing the PNG image.
    """
    W, H = 600, 820
    PITCH_TOP = 100
    PITCH_BOTTOM = H - 30
    PITCH_LEFT = 30
    PITCH_RIGHT = W - 30
    PITCH_W = PITCH_RIGHT - PITCH_LEFT
    PITCH_H = PITCH_BOTTOM - PITCH_TOP

    bg_color = (30, 30, 35)
    pitch_color = (45, 65, 45)
    line_color = (70, 100, 70)
    text_color = (240, 240, 240)
    dim_text = (180, 180, 180)

    img = Image.new('RGB', (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_rating = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
        font_number = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except:
        font_bold = font_name = font_small = font_title = font_subtitle = font_rating = font_number = ImageFont.load_default()

    # Header
    if match_info:
        home = match_info.get('home', {}).get('name', '')
        away = match_info.get('away', {}).get('name', '')
        tournament = match_info.get('tournament', {}).get('name', '')
        status = match_info.get('status', {})

        title = f"{home}  vs  {away}"
        bbox = draw.textbbox((0, 0), title, font=font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, 15), title, fill=text_color, font=font_title)

        subtitle_parts = [tournament]
        if status.get('ongoing'):
            subtitle_parts.append(f"LIVE {status.get('scoreStr', '')}")
        elif status.get('finished'):
            subtitle_parts.append(f"FT {status.get('scoreStr', '')}")
        subtitle = "  |  ".join(subtitle_parts)
        bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, 42), subtitle, fill=dim_text, font=font_subtitle)

    # Formation text
    formation = lineup_data.get('formation', '')
    form_text = f"Formation: {formation}"
    bbox = draw.textbbox((0, 0), form_text, font=font_subtitle)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 70), form_text, fill=dim_text, font=font_subtitle)

    # Pitch background
    _draw_rounded_rect(draw, (PITCH_LEFT, PITCH_TOP, PITCH_RIGHT, PITCH_BOTTOM), 12, pitch_color)

    # Pitch lines
    lw = 1
    # Halfway line
    mid_y = PITCH_TOP + PITCH_H // 2
    draw.line([(PITCH_LEFT, mid_y), (PITCH_RIGHT, mid_y)], fill=line_color, width=lw)
    # Center circle
    cr = 50
    draw.ellipse([W // 2 - cr, mid_y - cr, W // 2 + cr, mid_y + cr], outline=line_color, width=lw)
    # Penalty areas
    pa_w, pa_h = 180, 70
    draw.rectangle([W // 2 - pa_w // 2, PITCH_TOP, W // 2 + pa_w // 2, PITCH_TOP + pa_h], outline=line_color, width=lw)
    draw.rectangle([W // 2 - pa_w // 2, PITCH_BOTTOM - pa_h, W // 2 + pa_w // 2, PITCH_BOTTOM], outline=line_color, width=lw)
    # Goal areas
    ga_w, ga_h = 80, 30
    draw.rectangle([W // 2 - ga_w // 2, PITCH_TOP, W // 2 + ga_w // 2, PITCH_TOP + ga_h], outline=line_color, width=lw)
    draw.rectangle([W // 2 - ga_w // 2, PITCH_BOTTOM - ga_h, W // 2 + ga_w // 2, PITCH_BOTTOM], outline=line_color, width=lw)

    # Players
    PLAYER_RADIUS = 20
    MARGIN_X = 50
    MARGIN_Y = 40

    for player in lineup_data.get('starters', []):
        vl = player.get('verticalLayout', {})
        px = vl.get('x', 0.5)
        py = vl.get('y', 0.5)

        cx = PITCH_LEFT + MARGIN_X + (1.0 - px) * (PITCH_W - 2 * MARGIN_X)
        cy = PITCH_TOP + MARGIN_Y + (1.0 - py) * (PITCH_H - 2 * MARGIN_Y)

        # Player circle
        draw.ellipse(
            [cx - PLAYER_RADIUS, cy - PLAYER_RADIUS, cx + PLAYER_RADIUS, cy + PLAYER_RADIUS],
            fill=(50, 50, 55), outline=(100, 100, 110), width=2
        )

        # Shirt number
        number = player.get('shirtNumber', '?')
        bbox = draw.textbbox((0, 0), str(number), font=font_number)
        nw = bbox[2] - bbox[0]
        nh = bbox[3] - bbox[1]
        draw.text((cx - nw / 2, cy - nh / 2 - 2), str(number), fill=text_color, font=font_number)

        # Player name (below circle)
        name = player.get('name', '')
        parts = name.split()
        display_name = parts[-1] if len(parts) > 1 else name
        bbox = draw.textbbox((0, 0), display_name, font=font_name)
        nw = bbox[2] - bbox[0]
        draw.text((cx - nw / 2, cy + PLAYER_RADIUS + 3), display_name, fill=text_color, font=font_name)

        # Rating badge (top-right of circle)
        rating = player.get('performance', {}).get('rating')
        if rating:
            rating_str = f"{rating:.1f}" if isinstance(rating, float) else str(rating)
            r_color = _rating_color(float(rating))
            badge_w, badge_h = 30, 16
            bx = cx + PLAYER_RADIUS - 8
            by = cy - PLAYER_RADIUS - 4
            _draw_rounded_rect(draw, (bx, by, bx + badge_w, by + badge_h), 5, r_color)
            bbox = draw.textbbox((0, 0), rating_str, font=font_rating)
            rw = bbox[2] - bbox[0]
            draw.text((bx + (badge_w - rw) / 2, by + 1), rating_str, fill=(255, 255, 255), font=font_rating)

        # Season stats (goals/assists) below name
        perf = player.get('performance', {})
        goals = perf.get('seasonGoals', 0)
        assists = perf.get('seasonAssists', 0)
        if goals or assists:
            stat_y = cy + PLAYER_RADIUS + 18
            parts = []
            if goals:
                parts.append(("G:", (180, 180, 180), f"{goals}", (120, 210, 120)))
            if assists:
                parts.append(("A:", (180, 180, 180), f"{assists}", (120, 170, 230)))

            total_w = 0
            for label, _, val, _ in parts:
                total_w += draw.textbbox((0, 0), label + val, font=font_small)[2]
            if len(parts) > 1:
                total_w += 6
            sx = cx - total_w / 2

            for i, (label, lc, val, vc) in enumerate(parts):
                if i > 0:
                    sx += 6
                draw.text((sx, stat_y), label, fill=lc, font=font_small)
                lw = draw.textbbox((0, 0), label, font=font_small)[2]
                draw.text((sx + lw, stat_y), val, fill=vc, font=font_small)
                vw = draw.textbbox((0, 0), val, font=font_small)[2]
                sx += lw + vw

    # Save to BytesIO
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def get_lineup_image():
    """Get the lineup image for the current/next Barcelona match.
    
    Returns (BytesIO, caption_text) or (None, error_message).
    """
    team = get_fotmob_team_data()
    if not team:
        return None, "❌ Unable to fetch data from FotMob."

    overview = team.get('overview', {})
    next_match = overview.get('nextMatch')
    if not next_match:
        return None, "❌ No current match found."

    barca_lineup = overview.get('lastLineupStats')
    if not barca_lineup:
        return None, "❌ Lineup not available yet for this match."

    img_buf = generate_lineup_image(barca_lineup, match_info=next_match)

    home = next_match.get('home', {}).get('name', '?')
    away = next_match.get('away', {}).get('name', '?')
    tournament = next_match.get('tournament', {}).get('name', '')
    formation = barca_lineup.get('formation', '')
    caption = f"⚽ {home} vs {away} | {tournament}\n🔵🔴 Barcelona ({formation})"

    return img_buf, caption
