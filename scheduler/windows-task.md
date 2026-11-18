# Scheduling on Windows (Task Scheduler)

Run the aggregator every day at 07:45, writing the digest into the repo folder.

> **v2 note.** `run-briefing.sh` (network wait, retries, purge of consumed
> digests, hooks) is a bash script. On Windows, run it through **Git Bash** or
> **WSL** for the full v2 behaviour (program: `C:\Program Files\Git\bin\bash.exe`,
> argument: the path to `run-briefing.sh`). The plain-Python setup below still
> works: it writes `digests/<stamp>.md` and `feeds-digest.md`, but nothing is
> ever purged — clean `digests/` by hand from time to time.

Assuming the repo is at `%USERPROFILE%\bin\rss-news-watch` with a venv
(`py -m venv venv` then `venv\Scripts\python -m pip install feedparser`).

## Option A — PowerShell one-liner (registers the task)

```powershell
$repo = "$env:USERPROFILE\bin\rss-news-watch"
$action  = New-ScheduledTaskAction -Execute "$repo\venv\Scripts\python.exe" `
  -Argument "aggregate_feeds.py --feeds feeds.txt --out . --hours 48" `
  -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -Daily -At 7:45am
Register-ScheduledTask -TaskName "RSS News Watch" -Action $action -Trigger $trigger `
  -Description "Aggregate RSS feeds into a local digest for a scheduled LLM task"
```

To let a missed run fire when the machine wakes, after registering:

```powershell
$s = Get-ScheduledTask -TaskName "RSS News Watch"
$s.Settings.StartWhenAvailable = $true
Set-ScheduledTask -TaskName "RSS News Watch" -Settings $s.Settings
```

## Option B — GUI

1. Open **Task Scheduler** → **Create Task**.
2. **Triggers** → New → Daily at 07:45. Tick "Run task as soon as possible after
   a scheduled start is missed".
3. **Actions** → New → Program:
   `%USERPROFILE%\bin\rss-news-watch\venv\Scripts\python.exe`
   Arguments: `aggregate_feeds.py --feeds feeds.txt --out . --hours 48`
   Start in: `%USERPROFILE%\bin\rss-news-watch`
4. Test it once by hand and check `feeds-digest.log`.
