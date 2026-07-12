# The scheduled-task prompt

These two files are the prompt your assistant runs every morning. They are
identical in intent; pick your language:

- [`cowork-task.en.md`](cowork-task.en.md) — English
- [`cowork-task.fr.md`](cowork-task.fr.md) — French

Both are **templates**. Before using, replace:

| Placeholder     | With                                                            |
|-----------------|-----------------------------------------------------------------|
| `{{YOUR_NAME}}` | your first name                                                 |
| `{{DIGEST_DIR}}`| absolute path where `aggregate_feeds.py` writes the digest, e.g. `/Users/you/bin/rss-news-watch` |

The prompt is provider-agnostic — it just asks the model to read a local file,
dedup against a history file, and produce a briefing. Below is how to wire it
into common assistants.

## Claude Cowork

A Cowork scheduled task lives on disk at:

```
~/Claude/Scheduled/<task-name>/SKILL.md
```

The front-matter (`name`, `description`) plus the body **are** the task prompt.
Create the task from the Cowork UI (set the 08:00 daily schedule there), then
paste the filled-in prompt as the task's instructions. The connected folder must
include `{{DIGEST_DIR}}` so the task can read `feeds-digest.md`.

## ChatGPT (Tasks)

ChatGPT Tasks can't read a file on your disk directly. Two options:
- Put the digest somewhere the assistant can reach (a synced cloud folder it has
  a connector for), and point `{{DIGEST_DIR}}` at that, **or**
- Paste the day's `feeds-digest.md` into the task run. The rest of the prompt
  (dedup, formatting, domain structure) works unchanged.

## Any other LLM / self-hosted agent

Anything that can (a) run on a schedule and (b) read a local or cloud file works:
an [`llm`](https://llm.datasette.io/) CLI call from the same cron entry, an
n8n/Zapier flow, a small script that pipes `feeds-digest.md` into an API call.
The prompt body is the system/user instruction; the digest is the context.

## Why a local digest at all?

Hosted assistants block most newspaper RSS feeds (licensing). The aggregator
runs on **your** machine — no blocklist — and drops a plain file in your folder.
The assistant just reads a file you produced. See
[`../docs/how-it-works.md`](../docs/how-it-works.md).
