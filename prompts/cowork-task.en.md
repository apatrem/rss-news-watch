---
name: news-watch
description: News briefing from a local RSS digest — tech & AI, economy, politics, science, general news, AI coding agents. Runs daily or a few times a week.
---

<!--
  TEMPLATE TO CUSTOMIZE before pasting it into your scheduled task.
  Replace:
    {{YOUR_NAME}}   → your first name
    {{DIGEST_DIR}}  → ABSOLUTE path of the repo, where run-briefing.sh writes the
                      digests, e.g. /Users/you/bin/rss-news-watch
    {{SCHEDULE}}    → when the task runs, e.g. "every morning" or "Monday and Thursday mornings"
  That folder must be accessible/connected to your assistant (Cowork, etc.).
  Keep run-briefing.sh scheduled DAILY on your machine, whatever {{SCHEDULE}} is.
-->

Prepare {{YOUR_NAME}}'s news briefing ({{SCHEDULE}}), in English. Get today's date via bash if needed.

=== STEP 0 — WHAT MATERIAL IS AVAILABLE? (DO THIS FIRST) ===
The RSS digest can ONLY be produced on {{YOUR_NAME}}'s machine (network access to the feeds). You can't regenerate it. The machine produces one digest per day; the briefing may run less often, so finding several unconsumed digests is NORMAL.

  {{DIGEST_DIR}}/digests/YYYY-MM-DD-HHMM.md / .json / .log   ← timestamped digests, kept until consumed
  {{DIGEST_DIR}}/extras/YYYY-MM-DD-HHMM/                      ← optional material from hooks (if any)
  {{DIGEST_DIR}}/feeds-digest.md                              ← copy of the latest run only
  {{DIGEST_DIR}}/state.json                                   ← last_briefing_ok = date of the last briefing YOU actually produced
Cleaning is done by run-briefing.sh, never by you. Delete NOTHING in this folder.

Via bash, in this order:
1. Read state.json → `last_briefing_ok`. If missing, use the latest date in news-watch-history.md.
2. List digests/*.md and keep those whose timestamp is LATER than last_briefing_ok: the UNCONSUMED digests.
3. Pick the mode:

  A. NO unconsumed digest, and the latest one is older than ~24 h
     → nothing new. Do NOT brief (no WebSearch, no history write, no ack). Output ONLY:

     ---
     ⚠️ **Briefing skipped — no unconsumed RSS digest** (latest dated <date>).
     The digest must be regenerated on your machine (I have no network access to the feeds). Run this in a terminal, then re-run the briefing:

     ```bash
     cd {{DIGEST_DIR}}
     ./run-briefing.sh
     ```
     ---

  B. AT LEAST 1 unconsumed digest → BRIEFING (normal case). Follow the rest.

=== BRIEFING OVER ONE OR SEVERAL DAYS ===
Goal: cover in ONE briefing everything since the previous one, without drowning {{YOUR_NAME}}.
- Read ALL unconsumed digests, oldest first. They are large (~200 KB): work section by section with grep/sed, never load a whole file at once.
- DEDUPLICATE across digests: the same URL on two days = one bullet. A story that evolved over several days = ONE bullet with its final state, not a day-by-day chronology.
- Volume: 2-3 bullets per domain for a single digest, 4-6 for several.
- Group by THEME, never by day. Title: "Briefing <date of the oldest unconsumed digest> – <today>" (a single date for a single digest).
- 5-DAY CAP: if the gap exceeds 5 days, keep only what still matters today (decisions, figures, releases, ongoing stories); drop stale wires and "we'll know tomorrow" items already settled. Say so in one line at the top.
- If whole days have no digest (machine off), say so at the end: those days are lost, RSS feeds no longer carry them.
- In the history, each item keeps ITS OWN date (the date of the digest it came from), not today's.

=== PRIORITY INPUT: THE LOCAL DIGESTS ===
- Primary source for publishers you can't fetch (Guardian, BBC, Reuters, NYT, The Economist, Politico, FT, Rest of World, WSJ, Ars Technica, The Verge, Nature, Quanta…).
- The digest doesn't replace your judgment: select, verify, prioritize. WebSearch to go deeper or to verify.
- If extras/<stamp>/ exists, read its README or STATUS file first; it may hold full texts or data produced by {{YOUR_NAME}}'s hooks. Attribute every fact to the outlet that actually reported it.

=== SOURCE DIVERSITY (soft rule) ===
- At comparable relevance, prefer a source NOT yet cited in this briefing.
- Avoid citing the same outlet more than ~2-3 times across the briefing, unless the story truly justifies it.
- Relevance wins: for a scoop or a clearly better treatment, take it anyway.

=== FEED HEALTH ===
Read the digests/<stamp>.log of the consumed digests. If any line says "ERROR" or "EMPTY", add AT THE VERY END a short "⚠️ RSS feeds in error" section (feed + reason) and remind {{YOUR_NAME}} to fix the URL in feeds.txt. Otherwise write nothing about it.

=== AVOID REPETITION (BEFORE and AFTER) ===
Journal: {{DIGEST_DIR}}/news-watch-history.md (create it if missing).
1. AT THE START: read it. It lists items already covered (date, short title, URL).
2. SELECTION (soft): drop an item ONLY if already reported identically with nothing new. New development → include as "Follow-up:". Ambiguous → include.
3. AT THE END: append one line per reported item: "- [YYYY-MM-DD] short title — URL". ONE line per item, never multi-line blocks (the file is read in full every run and must stay grep-friendly). Two sentences allowed when you read a full text, to keep the key figures.
4. ARCHIVING (never delete a line): lines older than 30 days move out of the journal and are APPENDED to archives/news-watch-history-YYYY-MM.md for the month of THEIR date (create it with a "# News watch archive — YYYY-MM" title). Use a python read-modify-write: write the archive first, check the line count, only then remove the lines from the journal. Never read the archives during a briefing.

=== FINAL STEP — ACKNOWLEDGEMENT (MANDATORY, mode B only) ===
This is what lets run-briefing.sh purge the consumed digests. Forget it and they pile up; write it by mistake and unread material is lost. Do it LAST, after the history write; if the history write failed, do NOT ack.

```bash
cd {{DIGEST_DIR}}
python3 - <<'PY'
import json, os, datetime as dt, tempfile
p = "state.json"
d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
now = dt.datetime.now().replace(microsecond=0).isoformat()
d["last_briefing_window"] = {"from": d.get("last_briefing_ok", ""), "to": now}
d["last_briefing_ok"] = now
fd, tmp = tempfile.mkstemp(dir=".")
with os.fdopen(fd, "w", encoding="utf-8") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2); fh.write("\n")
os.replace(tmp, p)
print("ack:", now)
PY
```

=== CONTENT ===
Domains: 1. Tech & AI  2. Economy  3. Politics (national + international)  4. Science  5. General news  6. AI coding agents (dedicated section).

Complement with WebSearch as needed; you may also fetch these open tech feeds directly: Techmeme (https://www.techmeme.com/feed.xml), Ars Technica (https://feeds.arstechnica.com/arstechnica/index), The Verge (https://www.theverge.com/rss/index.xml), TechCrunch (https://techcrunch.com/feed/).

"AI CODING AGENTS" SECTION:
(a) Releases/updates of agentic coding models and tools over the covered period (Claude, OpenAI, Gemini, Mistral, DeepSeek, Qwen… / Claude Code, Codex, Cursor, Copilot, Windsurf, Cline, Aider…): version, date, what's new; verify via official changelogs.
(b) Security incidents affecting those tools (malicious extensions or packages, leaks), with what to check.
(c) Practical tools, skills and tips, always with a direct link. Nothing new → 1-2 durable references rather than inventing.

Paywall note: for paid outlets, use the title/blurb from the digest and verify through an open source. Never report an unverifiable fact; mark blurb-only facts as such.

Verify facts, dates, figures, versions, names.

Format (in the chat; only the journal, archives and state.json are files):
- Title "Briefing … – …".
- "Key points": 5-7 lines at the top (several digests) or 3 lines (one digest).
- One section per domain, "AI coding agents" separate. Bullets: key fact + short detail + linked source; prefix "Follow-up:" when relevant.
- "Coming up": dated deadlines of the next days spotted in the material.
- "Sources" at the end, then "⚠️ RSS feeds in error" only if needed.

Concise and factual. If a domain has nothing (after soft dedup), one line rather than inventing.
