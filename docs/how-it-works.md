# How it works

## The problem

Hosted assistants (Claude Cowork, ChatGPT, most cloud LLMs) **can't fetch many
newspaper RSS feeds**. They ship internal blocklists for licensing reasons, so a
task that tries to read `lemonde.fr/rss/...` or `lesechos.fr/rss/...` comes back
empty. That makes a "read my feeds and brief me" task unreliable.

## The workaround

Run the fetching **on your own machine**, where there is no blocklist. A tiny
Python script aggregates your feeds into plain local files. Your scheduled LLM
task then reads *those files* — no bypass, no scraping through the assistant,
just files you produced sitting in a folder the assistant can already see.

## The pipeline (v2)

```
07:30 every day — scheduler (launchd / cron / systemd / Task Scheduler)
  └─> run-briefing.sh
        ├─ purges digests the LLM task has already consumed (state.json)
        ├─ waits for the network (laptops waking up), retries if the digest is empty
        ├─ aggregate_feeds.py  → digests/<stamp>.md/.json/.log   (+ latest copy feeds-digest.*)
        │     window: 48 h, widened automatically after a gap (max 10 days)
        └─ optional hooks      → extras/<stamp>/                 (your own add-ons)

Daily, or e.g. Monday and Thursday — scheduled LLM task
  ├─ lists the UNCONSUMED digests (later than state.json → last_briefing_ok)
  ├─ none?  → says so in one line and stops
  ├─ reads them all, dedups across days and against news-watch-history.md
  ├─ briefs you in chat, grouped by theme
  ├─ appends the reported items to news-watch-history.md (archives lines > 30 days)
  └─ writes the acknowledgement last_briefing_ok in state.json
       (= stamp of the newest digest it read — never its own clock, see below)
```

The acknowledgement is the hinge of v2. The machine never deletes a digest the
task hasn't read, so:

- a day the computer was off, or the task didn't run, is caught up next time;
- the task can run less often than the collection (twice a week, say): the
  daily digests simply wait and are briefed together;
- `RETENTION_DAYS` (30) is a hard cap so nothing piles up forever.

**Why the ack is a digest stamp, not "now".** Digest names use the machine's
local time, but the LLM task may run in a sandbox on another time zone —
Claude Cowork's runs in UTC. An ack written with the task's clock would land
one or two hours early in Europe, and the morning's digest would look
"unconsumed": briefed twice, purged a cycle late. Using the stamp of the newest
digest read keeps everything on the machine's own clock.

## Why the script gets feeds the assistant can't

`aggregate_feeds.py` does three things a naive fetch doesn't:

1. **Sends a real browser User-Agent + header set.** Some servers return an empty
   body or a 403 HTML page to non-browser requests.
2. **Parses the raw bytes**, not the URL. feedparser otherwise rejects feeds that
   are mislabelled server-side (`Content-Type: text/html`).
3. **Falls back to `curl_cffi`** (Chrome TLS impersonation) when plain `urllib`
   is blocked by a Cloudflare-style anti-bot firewall. If `curl_cffi` isn't
   installed, it simply skips that fallback.

A broken feed never blocks the others — it's logged as `ERROR`/`EMPTY` in the
digest log, which the task surfaces so you can fix the URL in `feeds.txt`.

## Hooks

Every executable in `hooks/post-digest.d/` runs after a successful aggregation,
as `<hook> <stamp> <repo_dir>`, and should write to `extras/<stamp>/`. That
material is purged together with its digest once consumed. Use hooks for
anything you are entitled to fetch (open-access full texts, your own
subscriptions, APIs you have a key for). Personal hooks, cookies and keys are
git-ignored. See [`../hooks/post-digest.d/README.md`](../hooks/post-digest.d/README.md).

## Files

| File / folder                 | Written by        | Role                                              |
|-------------------------------|-------------------|---------------------------------------------------|
| `digests/<stamp>.md/.json/.log` | `aggregate_feeds.py` | the digests the task reads, kept until consumed |
| `feeds-digest.md/.json/.log`  | `aggregate_feeds.py` | copy of the latest run (handy to read by hand)  |
| `extras/<stamp>/`             | your hooks        | optional extra material                           |
| `state.json`                  | both              | `last_feed_run_ok` (script), `last_briefing_ok` (task) |
| `news-watch-history.md`       | the LLM task      | dedup journal, one line per reported item          |
| `archives/`                   | the LLM task      | history lines older than 30 days, by month        |
| `run-briefing.log`            | `run-briefing.sh` | what the wrapper did, run by run                  |

All of the above are git-ignored — they're personal or generated, not shipped.

## Maintenance commands

```bash
./run-briefing.sh --dry-run      # what would be purged right now (deletes nothing)
./run-briefing.sh --purge-only   # purge consumed material without fetching
tail -30 run-briefing.log        # last runs
```
