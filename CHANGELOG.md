# Changelog

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
