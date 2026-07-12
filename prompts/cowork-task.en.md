---
name: daily-news-watch-8am
description: Daily news watch at 8:00 AM — tech & AI, economy, politics, science, general news, with priority sources.
---

<!--
  TEMPLATE TO CUSTOMIZE before pasting it into your scheduled task.
  Replace:
    {{YOUR_NAME}}   → your first name
    {{DIGEST_DIR}}  → the folder where aggregate_feeds.py writes the digest,
                      e.g. /Users/you/bin/rss-news-watch  (ABSOLUTE path)
  That folder must be accessible/connected to your assistant (Cowork, etc.).
-->

Prepare a daily news watch for {{YOUR_NAME}}, in English. Get today's date via bash if needed.

=== PRIORITY INPUT: LOCAL RSS DIGEST ===
A script on {{YOUR_NAME}}'s machine aggregates their RSS feeds (including papers you can't fetch) and writes a local digest. BEFORE searching the web, read:
{{DIGEST_DIR}}/feeds-digest.md
(structured version: feeds-digest.json in the same folder)
- If it exists: it is the primary source for publishers (Guardian, BBC, Reuters, NYT, The Economist, Politico, FT, Rest of World, WSJ, Ars Technica, The Verge, Nature, Quanta, etc.).
- Check its freshness (header "RSS Digest — <date>"). If older than ~24h or missing, note it in one line and fall back to WebSearch.
- The digest does not replace your judgment: select, verify, prioritize. To go deeper on a headline, you may WebSearch it.

=== SOURCE DIVERSITY (soft rule) ===
Aim for a variety of sources across the briefing, without rigidity:
- At comparable relevance, prefer a source NOT yet cited in this briefing over one already used.
- Avoid citing the same outlet (e.g. "The Guardian", "NYT") more than ~2 times across the whole briefing, unless the story truly justifies it.
- On a topic covered by several sources, alternate origins day to day rather than always returning to the same one.
- EXCEPTION: relevance wins. For a scoop, an exclusive, or a clearly better treatment from an already-cited source, take it anyway — diversity is a preference, not a hard cap.

=== FEED HEALTH (to flag) ===
Also read: {{DIGEST_DIR}}/feeds-digest.log
Spot any "ERROR" or "EMPTY" line. If there are any, add AT THE VERY END a short "⚠️ RSS feeds in error" section: feed name + reason (e.g. "ERROR HTTP 403", "EMPTY"), and remind {{YOUR_NAME}} that they can fix the URL in feeds.txt in the same folder. If no feed is in error, write nothing about it.

=== AVOID REPETITION (BEFORE and AFTER the watch) ===
Persistent journal: {{DIGEST_DIR}}/news-watch-history.md
- Create the folder/file if missing (mkdir -p). If the path is not writable, create a dedicated subfolder in the available connected folder; note at the end of the watch where it was written.
1. AT THE START: read the journal. It lists news already covered (date, short title, URL).
2. SELECTION: SOFT rule — when in doubt, prefer inclusion.
   - Drop an item ONLY if already reported identically AND with no new element.
   - New development on an already-covered topic → include as "Follow-up:" with what's new.
   - New → include. Ambiguous near-duplicate → INCLUDE (possibly "Follow-up:").
3. AT THE END: append (without overwriting) one dated entry "- [YYYY-MM-DD] short title — URL" per reported item. Prune > 30 days.

=== WATCH CONTENT ===
Domains: 1. Tech & AI  2. Economy  3. Politics (national + international)  4. Science  5. General news  6. AI coding agents (dedicated section).

The local digest covers most sources. Complement with WebSearch as needed, and fetch these tech feeds directly if useful: Techmeme (https://www.techmeme.com/feed.xml), Ars Technica (https://feeds.arstechnica.com/arstechnica/index), The Verge (https://www.theverge.com/rss/index.xml), TechCrunch (https://techcrunch.com/feed/).

"AI CODING AGENTS" SECTION — every day:
(a) Releases/updates of agentic coding models and tools (24-48h): models/versions (Claude, OpenAI, Gemini, Mistral, DeepSeek, Qwen…) and tools (Claude Code, Cursor, Copilot, Windsurf, Cline, Aider, Devin…). Version, date, what's new; verify via official blogs/changelogs. Techmeme is a good entry point.
(b) Tools, "skills", practical tips for developers using AI agents, with a direct link. Sources: GitHub Trending, Hacker News, skill/agent repos, official blogs. Always the link. Nothing new → 1-2 durable reference resources rather than inventing.

Paywall note: The Economist, FT, NYT, WSJ (and others) are paid. If full content is inaccessible, use the title/blurb (the digest provides them) and verify via an open source. Never report an unverifiable fact.

Per domain: 2-3 notable, verified items not already reported. Verify facts, dates, figures, versions, names.

Format (in the chat; only the journal and the digest are files):
- Title with today's date.
- One section per domain (short bold title), "AI coding agents" separate.
- 2-3 bullets/section: key fact + short detail, linked source. Prefix "Follow-up:" for already-covered developments.
- A "Sources" section at the end.
- Then, IF AND ONLY IF feeds are in error, the "⚠️ RSS feeds in error" section.

Concise and factual. If a domain has nothing (after soft dedup), one line rather than inventing.
