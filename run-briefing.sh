#!/bin/bash
# run-briefing.sh — robust daily wrapper around aggregate_feeds.py (v2).
#
# Goal: there is ALWAYS unconsumed material waiting for the scheduled LLM task,
# even after a day the machine was off, or when the task only runs a few times
# a week (e.g. Monday and Thursday).
#
#   1. Timestamped outputs: digests/<stamp>.{md,json,log} (+ extras/<stamp>/ from hooks).
#   2. A digest is deleted ONLY once the LLM task has consumed it, i.e. when
#      state.json → last_briefing_ok is later than its timestamp
#      (hard cap: RETENTION_DAYS).
#   3. The RSS window widens automatically with the time since the last briefing,
#      to pick up whatever the feeds still carry after an absence.
#   4. Waits for the network, retries the aggregation, then runs optional hooks.
#
# Usage:   ./run-briefing.sh              normal run (what the scheduler calls)
#          ./run-briefing.sh --dry-run    show what would be purged, delete nothing
#          ./run-briefing.sh --purge-only purge consumed material, fetch nothing
#
# Writes: digests/, extras/, feeds-digest.*, state.json, run-briefing.log.
# Config via environment (all optional): PROBE_URL, RETENTION_DAYS, HOURS_MIN, HOURS_MAX.

set -u

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$DIR/venv/bin/python3"
[ -x "$PY" ] || PY="$(command -v python3)"
SCRIPT="$DIR/aggregate_feeds.py"
FEEDS="$DIR/feeds.txt"
DIGESTS_DIR="$DIR/digests"
EXTRAS_DIR="$DIR/extras"
HOOKS_DIR="$DIR/hooks/post-digest.d"
STATE="$DIR/state.json"
HISTORY="$DIR/news-watch-history.md"
WLOG="$DIR/run-briefing.log"

PROBE_URL="${PROBE_URL:-https://www.wikipedia.org}"   # any reliable HTTPS host
NET_WAIT_MAX=600        # max wait for the network: 10 min
NET_WAIT_STEP=20
MAX_TRIES=4             # aggregation attempts
TRY_BACKOFF=45          # seconds between attempts
HOURS_MIN="${HOURS_MIN:-48}"     # normal RSS window
HOURS_MAX="${HOURS_MAX:-240}"    # widest window after a long absence (10 days)
HOURS_MARGIN=12
RETENTION_DAYS="${RETENTION_DAYS:-30}"   # hard cap, even if never consumed

DRY_RUN=0
PURGE_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --dry-run)    DRY_RUN=1 ;;
    --purge-only) PURGE_ONLY=1 ;;
    -h|--help)    sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 64 ;;
  esac
done

log() { echo "$(date '+%Y-%m-%d %H:%M:%S')  $*" >> "$WLOG"; }

STAMP="$(date '+%Y-%m-%d-%H%M')"
log "=== run-briefing start (stamp $STAMP$([ "$DRY_RUN" -eq 1 ] && echo ', dry-run')) ==="
mkdir -p "$DIGESTS_DIR" "$EXTRAS_DIR"

# --------------------------------------------------------------------------
# state.json — shared memory between this script and the LLM task.
#   last_feed_run_ok : last successful aggregation      (written here)
#   last_briefing_ok : stamp of the newest digest the last briefing consumed,
#                      as YYYY-MM-DDTHH:MM:00 (written by the LLM task). It is
#                      derived from a digest file name, i.e. from THIS machine's
#                      clock — never from the task's own clock, whose time zone
#                      may differ (Cowork's sandbox runs in UTC).
#   last_briefing_window : stamps that briefing covered  (written by the LLM task)
# Fallback when state.json is missing: latest date in the history journal.
# --------------------------------------------------------------------------
state_get() {
  "$PY" - "$STATE" "$HISTORY" "$1" <<'PY'
import json, os, re, sys
state_path, hist_path, key = sys.argv[1:4]
val = ""
try:
    val = json.load(open(state_path, encoding="utf-8")).get(key) or ""
except Exception:
    pass
if not val and key == "last_briefing_ok" and os.path.exists(hist_path):
    dates = re.findall(r"^- \[(\d{4}-\d{2}-\d{2})\]", open(hist_path, encoding="utf-8").read(), re.M)
    if dates:
        val = max(dates) + "T08:00:00"
print(val)
PY
}

state_set() {
  "$PY" - "$STATE" "$1" "$2" <<'PY'
import json, os, sys, tempfile
path, key, value = sys.argv[1:4]
data = {}
if os.path.exists(path):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        data = {}
data[key] = value
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".")
with os.fdopen(fd, "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
os.replace(tmp, path)
PY
}

# --------------------------------------------------------------------------
# 1) Adaptive window: hours since the last consumed briefing.
# --------------------------------------------------------------------------
LAST_BRIEFING="$(state_get last_briefing_ok)"
HOURS="$HOURS_MIN"
if [ -n "$LAST_BRIEFING" ]; then
  GAP_H="$("$PY" -c '
import datetime as dt, sys
try:
    print(int((dt.datetime.now() - dt.datetime.fromisoformat(sys.argv[1])).total_seconds() // 3600))
except Exception:
    print(0)
' "$LAST_BRIEFING" 2>/dev/null || echo 0)"
  if [ "$GAP_H" -gt "$((HOURS_MIN - HOURS_MARGIN))" ]; then
    HOURS=$((GAP_H + HOURS_MARGIN))
    [ "$HOURS" -gt "$HOURS_MAX" ] && HOURS="$HOURS_MAX"
    log "${GAP_H} h since last_briefing_ok ($LAST_BRIEFING) — window widened to ${HOURS} h"
  else
    log "${GAP_H} h since last_briefing_ok — window ${HOURS} h"
  fi
else
  log "no last_briefing_ok yet — default window ${HOURS} h"
fi

# --------------------------------------------------------------------------
# 2) Conditional purge — only what has been consumed (or is past the hard cap).
# --------------------------------------------------------------------------
purge() {
  "$PY" - "$DIGESTS_DIR" "$EXTRAS_DIR" "${LAST_BRIEFING:-}" "$RETENTION_DAYS" "$DRY_RUN" <<'PY'
import datetime as dt, os, re, shutil, sys
digests_dir, extras_dir, last, retention, dry = sys.argv[1:6]
retention, dry = int(retention), dry == "1"
STAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{2})(\d{2})$")
try:
    consumed_through = dt.datetime.fromisoformat(last) if last else None
except Exception:
    consumed_through = None
hard_cutoff = dt.datetime.now() - dt.timedelta(days=retention)

def stamp_dt(stamp):
    m = STAMP_RE.match(stamp)
    if not m:
        return None
    d = dt.date.fromisoformat(m.group(1))
    return dt.datetime(d.year, d.month, d.day, int(m.group(2)), int(m.group(3)))

def reason(when):
    if when is None:
        return None
    if consumed_through and when <= consumed_through:
        return "consumed"
    if when < hard_cutoff:
        return f"older than {retention} days"
    return None

removed = kept = 0
stamps = sorted({os.path.splitext(f)[0] for f in os.listdir(digests_dir)
                 if f.endswith((".md", ".json", ".log"))}) if os.path.isdir(digests_dir) else []
for stamp in stamps:
    why = reason(stamp_dt(stamp))
    if why is None:
        kept += 1
        continue
    for ext in ("md", "json", "log"):
        p = os.path.join(digests_dir, f"{stamp}.{ext}")
        if os.path.exists(p):
            print(f"  - digests/{stamp}.{ext} ({why})")
            if not dry:
                os.remove(p)
    removed += 1

if os.path.isdir(extras_dir):
    for name in sorted(os.listdir(extras_dir)):
        p = os.path.join(extras_dir, name)
        if not os.path.isdir(p):
            continue
        why = reason(stamp_dt(name))
        if why is None:
            kept += 1
            continue
        print(f"  - extras/{name}/ ({why})")
        if not dry:
            shutil.rmtree(p)
        removed += 1

print(f"purge: {removed} item(s) {'would be removed' if dry else 'removed'}, {kept} kept (not consumed yet)")
PY
}

if [ "$DRY_RUN" -eq 1 ] || [ "$PURGE_ONLY" -eq 1 ]; then
  purge 2>&1 | tee -a "$WLOG"
else
  purge >> "$WLOG" 2>&1
fi
if [ "$PURGE_ONLY" -eq 1 ] || [ "$DRY_RUN" -eq 1 ]; then
  log "=== run-briefing end ($([ "$DRY_RUN" -eq 1 ] && echo dry-run || echo purge-only)) ==="
  exit 0
fi

# --------------------------------------------------------------------------
# 3) Wait for a working network (laptops waking up at 07:30 often aren't online yet).
# --------------------------------------------------------------------------
waited=0
until curl -sfI -m 8 "$PROBE_URL" >/dev/null 2>&1; do
  if [ "$waited" -ge "$NET_WAIT_MAX" ]; then
    log "gave up waiting for the network after ${waited}s — trying anyway"
    break
  fi
  sleep "$NET_WAIT_STEP"
  waited=$((waited + NET_WAIT_STEP))
done
log "network check done after ${waited}s"

# --------------------------------------------------------------------------
# 4) Aggregate, retrying if the digest comes out empty.
# --------------------------------------------------------------------------
digest_empty() {
  local f="$DIGESTS_DIR/$STAMP.md"
  # Match "0 articles" as a whole number: "440 articles" must NOT count as empty.
  [ ! -s "$f" ] || grep -qE "(^|[^0-9])0 articles aggregated" "$f"
}

n=1
while [ "$n" -le "$MAX_TRIES" ]; do
  log "attempt $n/$MAX_TRIES: aggregating (window ${HOURS} h)…"
  "$PY" "$SCRIPT" --feeds "$FEEDS" --out "$DIR" --hours "$HOURS" --stamp "$STAMP" >> "$WLOG" 2>&1
  if digest_empty; then
    log "attempt $n: EMPTY digest"
    [ "$n" -lt "$MAX_TRIES" ] && sleep "$TRY_BACKOFF"
    n=$((n + 1))
    continue
  fi
  log "attempt $n: OK (digests/$STAMP.md)"
  state_set last_feed_run_ok "$(date '+%Y-%m-%dT%H:%M:%S')"

  # 5) Optional hooks: every executable in hooks/post-digest.d/, in name order,
  #    called as  <hook> <stamp> <repo_dir>. Best-effort: a failing hook never
  #    fails the run. Hooks should write their output to extras/<stamp>/ so it
  #    is purged together with the digest once consumed.
  if [ -d "$HOOKS_DIR" ]; then
    for hook in "$HOOKS_DIR"/*; do
      [ -f "$hook" ] && [ -x "$hook" ] || continue
      log "hook $(basename "$hook")…"
      "$hook" "$STAMP" "$DIR" >> "$WLOG" 2>&1
      rc=$?   # capture first: any $(...) in the log line below would reset $?
      if [ "$rc" -eq 0 ]; then
        log "hook $(basename "$hook") OK"
      else
        log "hook $(basename "$hook") FAILED (code $rc) — ignored"
      fi
    done
  fi
  log "=== run-briefing end (OK) ==="
  exit 0
done

log "FAILED: digest still empty after $MAX_TRIES attempts"
log "=== run-briefing end (FAILED) ==="
exit 1
