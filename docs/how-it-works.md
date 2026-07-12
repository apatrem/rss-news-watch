# How it works

## The problem

Hosted assistants (Claude Cowork, ChatGPT, most cloud LLMs) **can't fetch many
newspaper RSS feeds**. They ship internal blocklists for licensing reasons, so a
task that tries to read `lemonde.fr/rss/...` or `lesechos.fr/rss/...` comes back
empty. That makes a "read my feeds and brief me" task unreliable.

## The workaround

Run the fetching **on your own machine**, where there is no blocklist. A tiny
Python script aggregates your feeds into a plain local file. Your scheduled LLM
task then reads *that file* — no bypass, no scraping through the assistant, just
a file you produced sitting in a folder the assistant can already see.

```
07:45  scheduler (launchd/cron/Task Scheduler)
         └─> aggregate_feeds.py
               ├─ downloads each feed (browser User-Agent, gzip, TLS-impersonation fallback)
               ├─ keeps items from the last 48h
               └─ writes:  feeds-digest.md   (readable digest — what the LLM reads)
                           feeds-digest.json (structured)
                           feeds-digest.log  (per-feed OK / ERROR / EMPTY)

08:00  scheduled LLM task (Cowork / ChatGPT / other)
         ├─ reads feeds-digest.md   (primary source)
         ├─ reads feeds-digest.log  (flags dead feeds back to you)
         ├─ dedups against news-watch-history.md
         ├─ optionally WebSearches to verify / go deeper
         └─ delivers the briefing in chat, then appends today's items to history
```

## Why the script gets feeds the assistant can't

`aggregate_feeds.py` does three things a naive fetch doesn't:

1. **Sends a real browser User-Agent + header set.** Some servers return an empty
   body or a 403 HTML page to non-browser requests.
2. **Parses the raw bytes**, not the URL. feedparser otherwise rejects feeds that
   are mislabelled server-side (`Content-Type: text/html`).
3. **Falls back to `curl_cffi`** (Chrome TLS impersonation) when plain `urllib`
   is blocked by a Cloudflare-style anti-bot firewall. If `curl_cffi` isn't
   installed, it simply skips that fallback.

A broken feed never blocks the others — it's logged as `ERROR`/`EMPTY` in
`feeds-digest.log`, which the morning task surfaces so you can fix the URL in
`feeds.txt`.

## Files the assistant reads vs. writes

| File                     | Produced by      | Role                                   |
|--------------------------|------------------|----------------------------------------|
| `feeds-digest.md`        | script (daily)   | primary input to the LLM task          |
| `feeds-digest.json`      | script (daily)   | structured version of the same         |
| `feeds-digest.log`       | script (daily)   | feed health, surfaced by the task      |
| `news-watch-history.md`  | the LLM task     | dedup journal, appended each run        |

`feeds.txt` is your active feed list (copied from one of the `*.example.txt`).
All of the above are git-ignored — they're personal/generated, not shipped.
