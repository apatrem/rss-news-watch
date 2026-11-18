# rss-news-watch

A tiny kit for a **daily news briefing produced by a scheduled LLM task** — Claude
Cowork, ChatGPT Tasks, or any assistant that can run on a schedule and read a file.

Hosted assistants can't fetch most newspaper RSS feeds (internal blocklists, for
licensing). So a small script runs **on your machine** — no blocklist — aggregates
your feeds into a local `feeds-digest.md`, and your scheduled task reads that file
each morning. No bypass; just a file you produced on your own disk.

> 🇫🇷 Version française : [README.fr.md](README.fr.md)

```
07:30 daily      scheduler → run-briefing.sh → aggregate_feeds.py → digests/<stamp>.md (+ .json + .log)
daily or 2×/week LLM task  → reads every unconsumed digest, dedups, briefs you, acknowledges
```

**v2** (see [CHANGELOG](CHANGELOG.md)): timestamped digests kept until the task has
read them, a robust wrapper (network wait, retries, adaptive window, safe purge),
optional hooks, history archiving — and the briefing can run less often than the
collection (e.g. Monday and Thursday).

See [`docs/how-it-works.md`](docs/how-it-works.md) for the full picture.

> **Using this yourself?** Fork the repo (or clone and re-init git) so it's *your*
> copy — then edit `feeds.txt`, the prompt placeholders, and the schedule freely.

## What's in here

| Path | What it is |
|------|-----------|
| `aggregate_feeds.py` | The aggregator. No hardcoded paths; portable. |
| `run-briefing.sh` | Daily wrapper: network wait, retries, adaptive window, purge of consumed digests, hooks. |
| `hooks/post-digest.d/` | Optional add-ons run after each digest (README + example). |
| `feeds.en.example.txt` | English/international feed list (copy to `feeds.txt`). |
| `feeds.fr.example.txt` | French/francophone feed list (copy to `feeds.txt`). |
| `prompts/` | The scheduled-task prompt, EN + FR, with a how-to-wire-it guide. |
| `scheduler/` | macOS (launchd), Linux (cron/systemd), Windows (Task Scheduler). |
| `docs/how-it-works.md` | Why the local digest exists and how the pieces fit. |

## Quick start (macOS example)

```bash
# 1. Get the code (fork first, then clone your fork so you can commit your own
#    feeds.txt tweaks; or just clone this one and re-init git)
git clone https://github.com/apatrem/rss-news-watch.git ~/bin/rss-news-watch
cd ~/bin/rss-news-watch

# 2. Python venv + dependency (macOS/Homebrew Python is externally-managed)
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt

# 3. Pick a feed list
cp feeds.en.example.txt feeds.txt      # or feeds.fr.example.txt

# 4. First run — writes digests/<stamp>.md (+ .json/.log) and feeds-digest.md here
./run-briefing.sh

# 5. Check the logs and fix any ERROR/EMPTY feed URL in feeds.txt
cat feeds-digest.log; tail run-briefing.log
```

Then schedule it (runs daily at 07:30 — keep it daily even if the briefing runs less often):

```bash
sed "s|{{REPO_DIR}}|$HOME/bin/rss-news-watch|g" \
  scheduler/macos-launchd.plist.template \
  > ~/Library/LaunchAgents/com.rss-news-watch.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.rss-news-watch.plist
# test immediately, without waiting for 07:30:
launchctl kickstart gui/$(id -u)/com.rss-news-watch
```

Linux / Windows: see [`scheduler/`](scheduler/).

## Wire up the LLM task

Open [`prompts/README.md`](prompts/README.md), fill in `{{YOUR_NAME}}`,
`{{DIGEST_DIR}}` and `{{SCHEDULE}}` in the EN or FR prompt, and paste it into
your assistant's scheduled task (set its schedule there: daily, or e.g. Monday
and Thursday). The connected folder must include the repo: the task reads
`digests/` and writes its acknowledgement to `state.json`.

## Customizing feeds

`feeds.txt` is one `Name | URL` per line; `#` comments and blank lines are
ignored. Add or remove freely, then re-run the script and check `feeds-digest.log`
— every feed reports `OK`, `ERROR`, or `EMPTY`. To narrow the window:
`--hours 24`.

## Notes

- The machine must be awake at 07:30 for the scheduler to fire; if asleep, the
  job runs at wake (launchd) or on next available run (systemd `Persistent`,
  Windows "run if missed"). A day missed entirely is caught up by the next
  briefing as far as the feeds still carry it (the window widens up to 10 days).
- Maintenance: `./run-briefing.sh --dry-run` (what would be purged) and
  `--purge-only`.
- A broken feed never blocks the others — it's just logged.
- `feeds.txt`, the digests, extras, logs, `state.json`, your history and archives,
  personal hooks, cookies and keys are git-ignored: they're personal or
  regenerated, never shipped.

## License

[MIT](LICENSE).
