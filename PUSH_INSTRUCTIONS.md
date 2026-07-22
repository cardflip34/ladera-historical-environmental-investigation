# Pushing this repo to GitHub — one step needed from you

Everything is committed locally on `main`, but **no git remote is configured** and the `gh` CLI is
not installed, so the final push could not be performed automatically.

## If the GitHub repo already exists
```bash
cd /Users/andystavros/Ladera-Ranch
git remote add origin https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
git push -u origin main
```
(macOS will use the osxkeychain credential helper — sign in with a GitHub personal access token if
prompted.)

## If it doesn't exist yet
Create an empty repo at github.com/new (suggest: **private** — the repo contains research working
files), then run the two commands above.

## Or with the GitHub CLI
```bash
brew install gh && gh auth login
gh repo create <REPO_NAME> --private --source=. --push
```

## What you'll be pushing (as of this run)
- `docs/california/` — **The California Report**: index + 11 sectioned HTML pages + `California_Report.pdf` (66 pp, condensed from 288)
- `media/video/SCRIPT_california.md` — the 7–8 min narration script
- `media/broll/` — B-roll index + 9 boards
- `research/` — all graded findings incl. the GLO patent, EnviroStor/GeoTracker first-hand reads, CDNC press record, verified school rosters
- `PLAN_CALIFORNIA_REPORT.md` + `docs/plan_california_report.{html,pdf}` — the plan of record
