# Barcelona Match Reminder

Me and my friends are big fans of FC Barcelona. We always watch the matches together(virtually, each in a different time zone). Since the Pandemic, one of always had to Send a message about the upcoming match. I thought it would be a good idea to automate this process. So I created this telegram bot. It uses `Football API` to get the upcoming matches and sends a message to the group chat,, with the time zone of each of us.  



# How to use

## TMUX

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



## Python Environment
I use the same env as the newsum bot.
```bash
source ../newsum/telegram/bin/activate
```