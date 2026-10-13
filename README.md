# Weekly Business Review

One static page for the weekly business review call, for MAIA and AVIA: scorecard, pacing against plan, tasks, issues board, hires, inventory, customer service, creative, run of show and definitions.

Vercel serves `public/` as-is. There is no build step on Vercel. Every push to `main` redeploys the site.

## Updated every Monday

Two scheduled Claude tasks run every Monday at 7:00 am Eastern:

1. **WBR weekly update** pulls the week that just ended from Triple Whale, Shopify, Commslayer, ClickUp and the creative strategy dashboard into the page database.
2. **WBR customer service update** does the same for Commslayer and Quo.

Each one finishes by exporting the page database, running `scripts/export.py`, and pushing one commit that changes `public/data/db.json`. Vercel deploys that push. The banner at the top of the site shows the date of the snapshot it is displaying, and the Definitions tab lists what each update could and could not pull.

If a Monday run fails, the site keeps showing the previous snapshot until the next successful run.

## What is in this repository

| Path | What it is |
|---|---|
| `public/index.html` | The built page. This is what Vercel serves. |
| `public/data/db.json` | The data snapshot the page displays. Rewritten by the Monday updates. |
| `src/weekly-business-review.html` | The page source: styles, markup and script in one file, written in the Claude artifact format (no `<html>`, `<head>` or `<body>`). Edit this file. |
| `src/standalone-shim.js` | The data layer used outside Claude. It reads the snapshot and serves it read-only. |
| `scripts/build_page.py` | Wraps the source in a normal HTML document, adds the shim, and writes `public/index.html`. |
| `scripts/export.py` | Turns an export of the page database into `public/data/db.json`. |
| `docs/data-model.md` | The collections and documents the page reads. |
| `vercel.json` | Tells Vercel to serve `public/` and asks search engines not to index the site. |

**The snapshot is committed here on purpose.** `public/data/db.json` holds revenue, the cash plan, supplier payments and per-person numbers. Anyone who can read this repository or open the Vercel URL can read it. It never holds customer names, phone numbers, addresses or card details, and `scripts/export.py` stops if an export appears to contain any.

## Deploy on Vercel (one time)

1. Vercel → **Add New → Project → Import** this repository.
2. Framework Preset: **Other**. Leave Build Command empty. The output directory (`public`) comes from `vercel.json`.
3. Optional: **Settings → Deployment Protection** limits who can open the site.

## Read-only by design

On Vercel the page is a read-only copy. Tasks, targets, owner notes, stock counts and cash balances are edited on the Claude page, where they save to its shared database, and reach this copy with the next snapshot.

## Refreshing the data by hand

From an export of the page database (one folder per collection, one JSON file per document):

```bash
python3 -I scripts/export.py path/to/export 2026-10-12
git add public/data/db.json && git commit -m "Refresh data" && git push
```

A collection missing from the export keeps what the snapshot already has. Git keeps every earlier snapshot in the history.

## Changing the page

```bash
# edit src/weekly-business-review.html, then
python3 scripts/build_page.py
git add -A && git commit -m "Describe the change" && git push
```

The same source file is what gets published as the Claude page, so the two stay identical. To preview locally:

```bash
python3 -m http.server 8000 --directory public
```

## Weeks

Every tab uses ISO calendar weeks, Monday to Sunday, labelled by week number (W40, W41).
