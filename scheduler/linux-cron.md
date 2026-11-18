# Scheduling on Linux (cron)

Run `run-briefing.sh` every day at 07:30. It waits for the network, aggregates
into `digests/`, purges what the LLM task has already consumed, and runs your
optional hooks. Keep it daily even if the LLM task runs only a few times a week.

Assuming the repo is at `~/bin/rss-news-watch` with a venv (see the main README):

```bash
crontab -e
```

Add this line (cron uses the machine's local time):

```cron
30 7 * * * /bin/bash "$HOME/bin/rss-news-watch/run-briefing.sh"
```

Notes:
- `cron` needs the machine awake at 07:30. For laptops that sleep, use
  [`anacron`](https://linux.die.net/man/8/anacron) or a `systemd` timer with
  `Persistent=true` so a missed run fires at next wake.
- Verify with `./run-briefing.sh` once by hand first, then check `run-briefing.log`
  and `feeds-digest.log`.

## systemd timer alternative (fires on wake if missed)

`~/.config/systemd/user/rss-news-watch.service`:

```ini
[Unit]
Description=RSS news watch aggregator

[Service]
Type=oneshot
WorkingDirectory=%h/bin/rss-news-watch
ExecStart=/bin/bash %h/bin/rss-news-watch/run-briefing.sh
```

`~/.config/systemd/user/rss-news-watch.timer`:

```ini
[Unit]
Description=Run RSS news watch daily at 07:30

[Timer]
OnCalendar=*-*-* 07:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now rss-news-watch.timer
```
