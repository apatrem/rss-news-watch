# rss-news-watch

A tiny kit for a **daily news briefing produced by a scheduled LLM task** — Claude
Cowork, ChatGPT Tasks, or any assistant that can run on a schedule and read a file.

Hosted assistants can't fetch most newspaper RSS feeds (internal blocklists, for
licensing). So a small script runs **on your machine** — no blocklist — aggregates
your feeds into a local `feeds-digest.md`, and your scheduled task reads that file
each morning. No bypass; just a file you produced on your own disk.

> 🇫🇷 Version française : [README.fr.md](README.fr.md)

```
07:45  scheduler → aggregate_feeds.py → feeds-digest.md (+ .json + .log)
08:00  LLM task  → reads the digest, dedups against history, briefs you in chat
```

See [`docs/how-it-works.md`](docs/how-it-works.md) for the full picture.

## What's in here

| Path | What it is |
|------|-----------|
| `aggregate_feeds.py` | The aggregator. No hardcoded paths; portable. |
| `feeds.en.example.txt` | English/international feed list (copy to `feeds.txt`). |
| `feeds.fr.example.txt` | French/francophone feed list (copy to `feeds.txt`). |
| `prompts/` | The scheduled-task prompt, EN + FR, with a how-to-wire-it guide. |
| `scheduler/` | macOS (launchd), Linux (cron/systemd), Windows (Task Scheduler). |
| `docs/how-it-works.md` | Why the local digest exists and how the pieces fit. |

## Quick start (macOS example)

```bash
# 1. Get the code
git clone https://github.com/apatrem/rss-news-watch.git ~/bin/rss-news-watch
cd ~/bin/rss-news-watch

# 2. Python venv + dependency (macOS/Homebrew Python is externally-managed)
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt

# 3. Pick a feed list
cp feeds.en.example.txt feeds.txt      # or feeds.fr.example.txt

# 4. First run — writes feeds-digest.md / .json / .log here
./venv/bin/python aggregate_feeds.py

# 5. Check the log and fix any ERROR/EMPTY feed URL in feeds.txt
cat feeds-digest.log
```

Then schedule it (runs daily at 07:45):

```bash
sed "s|{{REPO_DIR}}|$HOME/bin/rss-news-watch|g" \
  scheduler/macos-launchd.plist.template \
  > ~/Library/LaunchAgents/com.rss-news-watch.plist
launchctl load ~/Library/LaunchAgents/com.rss-news-watch.plist
# test immediately, without waiting for 07:45:
launchctl start com.rss-news-watch
```

Linux / Windows: see [`scheduler/`](scheduler/).

## Wire up the LLM task

Open [`prompts/README.md`](prompts/README.md), fill in `{{YOUR_NAME}}` and
`{{DIGEST_DIR}}` in the EN or FR prompt, and paste it into your assistant's
scheduled task (set the 08:00 daily schedule there). The connected folder must
include the repo so the task can read `feeds-digest.md`.

## Customizing feeds

`feeds.txt` is one `Name | URL` per line; `#` comments and blank lines are
ignored. Add or remove freely, then re-run the script and check `feeds-digest.log`
— every feed reports `OK`, `ERROR`, or `EMPTY`. To narrow the window:
`--hours 24`.

## Notes

- The machine must be awake at 07:45 for the scheduler to fire; if asleep, the
  job runs at wake (launchd) or on next available run (systemd `Persistent`,
  Windows "run if missed").
- A broken feed never blocks the others — it's just logged.
- `feeds.txt`, the digests, logs, and your dedup history are git-ignored: they're
  personal or regenerated, not shipped.

## License

[MIT](LICENSE).
