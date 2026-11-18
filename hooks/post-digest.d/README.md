# Post-digest hooks

Every **executable** file in this folder runs after a successful aggregation,
in name order, as:

```
<hook> <stamp> <repo_dir>
```

- `<stamp>` is the run timestamp (`YYYY-MM-DD-HHMM`), the same as `digests/<stamp>.md`.
- Write your output to `extras/<stamp>/`: it is then purged together with the
  digest once the LLM task has consumed it (see `run-briefing.sh`).
- Hooks are best-effort: a failing hook is logged in `run-briefing.log` and
  never fails the run.

Typical uses: fetch the full text of a few articles **from a source you are
entitled to read** (your own subscription, an open-access site, an API you have
a key for), extract chart data, translate, summarise…

Keep anything personal out of the repository: cookies, API keys and personal
hooks are git-ignored by default (only `README.md` and `*.example` files in this
folder are tracked).

See `00-example.sh.example` for a minimal template.
