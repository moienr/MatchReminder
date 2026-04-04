# Barcelona Match Reminder

Me and my friends are big fans of FC Barcelona. We always watch the matches together (virtually, each in a different time zone). Since the Pandemic, one of us always had to send a message about the upcoming match. I thought it would be a good idea to automate this process. So I created this Telegram bot. It uses `Football API` and `FotMob` to get upcoming matches and sends a message to the group chat with the time zone of each of us.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show available commands |
| `/nextmatch` | Get the next Barça match with kick-off times (TEH, VANC, CET) |
| `/todaymatch` | Check if Barça plays today — pins the match info if yes |
| `/score` | Get the latest match score or live score |
| `/table` | Get the current La Liga table (all 20 teams) |
| `/lineup` | Get a graphic lineup image for the current match |

## Features

- **Multi-API support**: Uses [football-data.org](https://www.football-data.org/) for La Liga & Champions League, and [FotMob](https://www.fotmob.com/) for Copa del Rey and other competitions
- **Lineup image**: Generates a pitch graphic with player positions, shirt numbers, ratings, and season stats (goals/assists)
- **Multi-timezone**: Shows kick-off times in Tehran, Vancouver, and CET
- **Daily reminder**: Automatically checks at 10:00 AM CET every day and notifies all groups whether Barça plays or not, pinning the match info
- **Live score**: Fetches live or latest match results with win/loss/draw indicators

## How to use

### TMUX

Run:
```bash
tmux new-session -d -s barcabot "cd /root/code/MatchReminder && source ../newsum/telegram/bin/activate && python main.py"
```

Kill:
```bash
tmux kill-session -t barcabot
```

Observe:
```bash
tmux attach-session -t barcabot
```

### Python Environment
I use the same env as the newsum bot.
```bash
source ../newsum/telegram/bin/activate
```
