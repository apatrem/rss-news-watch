# Changelog

## v2.1 — 2026-11-18

- **Time-zone-safe acknowledgement.** The task now acks with the stamp of the
  newest digest it read instead of its own clock (Cowork's sandbox runs in UTC,
  which made the ack land 1-2 h early in Europe and the morning digest look
  unconsumed). The ack also refuses to move backwards.
- **"Nothing new" mode clarified.** No unconsumed digest now always skips the
  briefing, with two messages: already briefed (latest digest < 24 h) or
  collection didn't run (older).
- **Anti-bot fallback made consistent.** The `curl_cffi` fallback no longer
  forces the fixed User-Agent over its own TLS fingerprint (a classic bot
  tell). Some sites (Usine Digitale, Usine Nouvelle) still block
  intermittently; they are logged as ERROR when they do. Rest of World (blocks
  every automated reader) is commented out in both example lists; Reuters
  mention removed from the EN prompt.
- **Small fixes.** Failed hooks log their real exit code; the example hook no
  longer fails on a digest with 0 articles.

## v2 — 2026-11

- **Timestamped digests.** Each run writes `digests/YYYY-MM-DD-HHMM.{md,json,log}`;
  `feeds-digest.*` remains as a copy of the latest run. New `--stamp` option.
- **`run-briefing.sh` wrapper.** Waits for the network, retries an empty
  aggregation, widens the RSS window after a gap, runs optional hooks.
- **Acknowledgement + safe purge.** The LLM task writes `last_briefing_ok` in
  `state.json`; the wrapper only deletes digests older than that (30-day hard cap).
  Missed days are caught up instead of lost.
- **Runs less often than daily.** Collection stays daily; the briefing can run
  e.g. twice a week and covers all unconsumed digests, grouped by theme.
- **Hooks.** `hooks/post-digest.d/` for your own add-ons, writing to `extras/<stamp>/`.
- **History archiving.** Lines older than 30 days move to `archives/` instead of
  being deleted.
- **Prompts rewritten** (EN + FR) for the above: "no new digest" mode,
  multi-day briefing, acknowledgement, archiving, "Key points" and "Coming up".
- Schedulers updated (launchd, cron, systemd); `.gitignore` covers state,
  history, archives, extras, cookies and keys.

## v1 — 2026-07

- Initial release: `aggregate_feeds.py`, example feed lists, prompts, schedulers.
