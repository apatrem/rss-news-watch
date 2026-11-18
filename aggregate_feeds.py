#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggregate_feeds.py — RSS aggregator for a scheduled LLM news briefing.

Idea: hosted LLMs (Claude Cowork, ChatGPT Tasks, etc.) can't fetch most newspaper
RSS feeds (internal blocklists, for licensing reasons). This script runs on YOUR
machine (no blocklist), reads your feeds, and writes a local digest into a folder
your LLM task can read. The scheduled LLM task then reads that file — no bypass,
just a file dropped on your own disk.

Outputs (in OUTPUT_DIR):
  - digests/YYYY-MM-DD-HHMM.{md,json,log} : timestamped ORIGINAL of each run, kept until
      the LLM task has consumed it (see run-briefing.sh). This is what lets the task
      catch up after a day off, or run only a few times a week. Never purged here.
  - feeds-digest.md    : copy of the latest run — readable digest
  - feeds-digest.json  : copy of the latest run, structured
  - feeds-digest.log   : copy of the latest run — per-feed status (OK / item count / errors)

Usage:
  python3 aggregate_feeds.py
  python3 aggregate_feeds.py --hours 48 --feeds /path/feeds.txt --out "/path/output"
  python3 aggregate_feeds.py --stamp 2026-08-26-0730     # force the run timestamp

Config:
  Output dir default = RSS_WATCH_DIR env var, else the script's own directory.
  Feed list default  = feeds.txt next to this script (copy one of the *.example.txt).

Dependency: feedparser  ->  pip install feedparser (in a venv)
Optional:   curl_cffi   ->  pip install curl_cffi (helps past anti-bot firewalls)
"""

import argparse
import datetime as dt
import gzip
import html
import json
import os
import re
import ssl
import sys
import time
import zlib
import urllib.error
import urllib.request
from urllib.parse import urlparse

try:
    import feedparser
except ImportError:
    sys.stderr.write(
        "ERROR: the 'feedparser' module is missing.\n"
        "Install it in a venv:  python3 -m venv venv && ./venv/bin/python -m pip install feedparser\n"
    )
    sys.exit(1)

# curl_cffi (optional): mimics Chrome's TLS fingerprint to get past anti-bot
# firewalls (e.g. Cloudflare, as used by some paywalled papers). If absent, we
# fall back to urllib.
#   Install:  ./venv/bin/python -m pip install curl_cffi
try:
    from curl_cffi import requests as cffi_requests  # type: ignore
    HAVE_CFFI = True
except ImportError:
    HAVE_CFFI = False

# --- Default paths ------------------------------------------------------------
# Output goes to RSS_WATCH_DIR if set, otherwise next to this script. That keeps
# the repo portable: no hardcoded home directory or username.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.environ.get("RSS_WATCH_DIR", SCRIPT_DIR)
DEFAULT_FEEDS = os.path.join(SCRIPT_DIR, "feeds.txt")

# Browser User-Agent: some sites return an empty response to non-browser
# requests. This helps retrieve their feeds.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text, limit=280):
    """Clean an HTML summary into short text."""
    if not text:
        return ""
    text = html.unescape(TAG_RE.sub(" ", text))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def load_feeds(path):
    """
    Read feeds.txt. Accepted per-line formats:
      URL
      Name | URL
      # comment (line ignored)
    An END-of-line comment is also tolerated: "... # blabla".
    Returns a list of (name, url).
    """
    feeds = []
    if not os.path.exists(path):
        sys.stderr.write(f"ERROR: feed list not found: {path}\n")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # Strip a trailing " # comment" without breaking a "#..." fragment
            # stuck to the URL: we only split on " #".
            if " #" in line:
                line = line.split(" #", 1)[0].strip()
            if not line:
                continue
            if "|" in line:
                name, url = line.split("|", 1)
                name, url = name.strip(), url.strip()
            else:
                url = line.strip()
                name = urlparse(url).netloc.replace("www.", "")
            # Guard: remove any residual whitespace/control character.
            url = "".join(url.split())
            if url:
                feeds.append((name, url))
    return feeds


def entry_datetime(entry):
    """Return a UTC datetime for the entry, or None."""
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            try:
                return dt.datetime.fromtimestamp(time.mktime(t), tz=dt.timezone.utc)
            except (TypeError, ValueError, OverflowError):
                continue
    return None


def fetch_bytes(url, timeout=20):
    """
    Download the feed ourselves (browser UA + gzip). We then hand the BYTES to
    feedparser: this avoids feedparser rejecting a feed mislabelled server-side
    ('Content-Type: text/html' instead of 'application/xml'), and lets us send a
    real User-Agent for sites that filter non-browser requests.
    """
    # A real browser's header set: some servers (e.g. paywalled papers) return a
    # 403 + HTML page if the request doesn't look like a real browser session,
    # and that HTML page is what used to crash the parser ("mismatched tag").
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/rss+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
        },
    )
    ctx = ssl.create_default_context()

    def via_urllib():
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            data = resp.read()
            enc = (resp.headers.get("Content-Encoding") or "").lower()
        if "gzip" in enc:
            try:
                data = gzip.decompress(data)
            except OSError:
                pass
        elif "deflate" in enc:
            try:
                data = zlib.decompress(data)
            except zlib.error:
                data = zlib.decompress(data, -zlib.MAX_WBITS)
        return data

    def via_cffi():
        # No custom headers here: impersonate="chrome" sends a header set that
        # matches its TLS fingerprint. Forcing our fixed (older) Chrome User-Agent
        # on top of a newer fingerprint is exactly the mismatch anti-bot firewalls
        # look for. (Some sites still block intermittently whatever we send, e.g.
        # Usine Digitale / Usine Nouvelle: they then show up as ERROR in the log.)
        r = cffi_requests.get(
            url, impersonate="chrome",
            timeout=timeout, allow_redirects=True,
        )
        if r.status_code >= 400:
            raise urllib.error.HTTPError(url, r.status_code, "via curl_cffi", None, None)
        return r.content

    # Try urllib first (accepted by most feeds), then curl_cffi as a fallback
    # (Chrome TLS impersonation, to get past Cloudflare-type firewalls). If both
    # fail, we re-raise the more informative error. Each feed thus takes the path
    # that works for it — without one method breaking another.
    if not HAVE_CFFI:
        return via_urllib()

    try:
        return via_urllib()
    except Exception as e_urllib:  # noqa: BLE001
        try:
            return via_cffi()
        except Exception:  # noqa: BLE001
            raise e_urllib


def fetch_feed(name, url):
    """Fetch one feed. Returns (items, status_str)."""
    # We download ourselves then parse the bytes (robust method). HTTP errors
    # (403, 404...) are surfaced as-is: no point parsing an HTML error page,
    # which produced false "mismatched tag" errors.
    try:
        raw = fetch_bytes(url)
        parsed = feedparser.parse(raw)
    except urllib.error.HTTPError as exc:
        hint = " (anti-bot: User-Agent/headers refused)" if exc.code == 403 else ""
        return [], f"ERROR HTTP {exc.code}{hint}"
    except Exception as exc:  # noqa: BLE001
        # Fallback for transient network errors: let feedparser try the URL.
        try:
            parsed = feedparser.parse(url, agent=USER_AGENT)
        except Exception as exc2:  # noqa: BLE001
            return [], f"ERROR fetch ({exc} | fallback: {exc2})"

    if getattr(parsed, "bozo", 0) and not parsed.entries:
        reason = getattr(parsed, "bozo_exception", "unreadable format")
        return [], f"ERROR parse ({reason})"

    if not parsed.entries:
        return [], "EMPTY (0 entries — check URL)"

    items = []
    for e in parsed.entries:
        when = entry_datetime(e)
        items.append(
            {
                "source": name,
                "title": strip_html(e.get("title", "(no title)"), 240),
                "link": e.get("link", ""),
                "published": when.isoformat() if when else None,
                "_dt": when,
                "summary": strip_html(e.get("summary", ""), 280),
            }
        )
    return items, f"OK ({len(items)} entries)"


def within_window(item, cutoff):
    """Keep the item if inside the window. If no date, keep it (cautious)."""
    if item["_dt"] is None:
        return True
    return item["_dt"] >= cutoff


def main():
    ap = argparse.ArgumentParser(description="RSS aggregator for a scheduled LLM briefing.")
    ap.add_argument("--hours", type=int, default=48, help="Time window in hours (default 48).")
    ap.add_argument("--feeds", default=DEFAULT_FEEDS, help="Path to feeds.txt.")
    ap.add_argument("--out", default=DEFAULT_OUT, help="Output directory.")
    ap.add_argument("--stamp", default=None,
                    help="Run timestamp YYYY-MM-DD-HHMM (default: now). Names the files in digests/.")
    args = ap.parse_args()

    out_dir = os.path.expanduser(args.out)
    os.makedirs(out_dir, exist_ok=True)
    stamp = args.stamp or dt.datetime.now().strftime("%Y-%m-%d-%H%M")
    digests_dir = os.path.join(out_dir, "digests")
    os.makedirs(digests_dir, exist_ok=True)

    cutoff = dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(hours=args.hours)
    feeds = load_feeds(args.feeds)

    all_items = []
    log_lines = []
    now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    log_lines.append(f"Run: {now_str} | window: {args.hours}h | {len(feeds)} feeds")
    log_lines.append("-" * 60)

    for name, url in feeds:
        items, status = fetch_feed(name, url)
        kept = [it for it in items if within_window(it, cutoff)]
        all_items.extend(kept)
        log_lines.append(f"[{status:28}] {len(kept):>3} kept | {name} | {url}")

    # Sort by descending date (undated ones at the end).
    all_items.sort(key=lambda it: it["_dt"] or dt.datetime.min.replace(tzinfo=dt.timezone.utc), reverse=True)

    # --- Write Markdown -------------------------------------------------------
    md = []
    md.append(f"# RSS Digest — {now_str}")
    md.append("")
    md.append(f"_Window: last {args.hours} h. {len(all_items)} articles aggregated from {len(feeds)} feeds._")
    md.append("")
    by_source = {}
    for it in all_items:
        by_source.setdefault(it["source"], []).append(it)
    for source in sorted(by_source.keys(), key=str.lower):
        md.append(f"## {source}")
        md.append("")
        for it in by_source[source]:
            date_str = (it["published"] or "")[:16].replace("T", " ")
            md.append(f"- **[{date_str}]** {it['title']} — {it['link']}")
            if it["summary"]:
                md.append(f"  - {it['summary']}")
        md.append("")
    md_text = "\n".join(md)

    # --- Write JSON -----------------------------------------------------------
    json_items = []
    for it in all_items:
        j = {k: v for k, v in it.items() if k != "_dt"}
        json_items.append(j)
    json_text = json.dumps(
        {
            "generated": dt.datetime.now().isoformat(),
            "stamp": stamp,
            "window_hours": args.hours,
            "item_count": len(all_items),
            "items": json_items,
        },
        ensure_ascii=False,
        indent=2,
    )

    # --- Write log ------------------------------------------------------------
    log_text = "\n".join(log_lines)

    # --- Write: timestamped original in digests/ + latest copy at the root -----
    for ext, text in (("md", md_text), ("json", json_text), ("log", log_text + "\n")):
        for path in (os.path.join(digests_dir, f"{stamp}.{ext}"),
                     os.path.join(out_dir, f"feeds-digest.{ext}")):
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)

    # Console output (useful on the first test run).
    print(log_text)
    print("-" * 60)
    print(f"OK → {os.path.join(digests_dir, stamp + '.md')} ({len(all_items)} articles)")
    print(f"     latest copy → {os.path.join(out_dir, 'feeds-digest.md')}")


if __name__ == "__main__":
    main()
