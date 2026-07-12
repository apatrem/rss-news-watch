# Scheduling on Linux (cron)

Run the aggregator every day at 07:45, writing the digest into the repo folder.

Assuming the repo is at `~/bin/rss-news-watch` with a venv (see the main README):

```bash
crontab -e
```

Add this line (cron uses the machine's local time):

```cron
45 7 * * * cd "$HOME/bin/rss-news-watch" && ./venv/bin/python aggregate_feeds.py --feeds feeds.txt --out . --hours 48 >> launchd-out.log 2>&1
```

Notes:
- `cron` needs the machine awake at 07:45. For laptops that sleep, use
  [`anacron`](https://linux.die.net/man/8/anacron) or a `systemd` timer with
  `Persistent=true` so a missed run fires at next wake.
- Verify with `./venv/bin/python aggregate_feeds.py` once by hand first, then
  check `feeds-digest.log`.

## systemd timer alternative (fires on wake if missed)

`~/.config/systemd/user/rss-news-watch.service`:

```ini
[Unit]
Description=RSS news watch aggregator

[Service]
Type=oneshot
WorkingDirectory=%h/bin/rss-news-watch
ExecStart=%h/bin/rss-news-watch/venv/bin/python aggregate_feeds.py --feeds feeds.txt --out . --hours 48
```

`~/.config/systemd/user/rss-news-watch.timer`:

```ini
[Unit]
Description=Run RSS news watch daily at 07:45

[Timer]
OnCalendar=*-*-* 07:45:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now rss-news-watch.timer
```
