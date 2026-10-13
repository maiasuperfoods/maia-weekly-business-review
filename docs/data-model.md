# Data model

The page reads a small document database: collections of JSON documents. Inside Claude this is the artifact database. On Vercel it is one file, `public/data/db.json`:

```json
{ "exportedAt": "YYYY-MM-DD", "collections": { "<collection>": { "<docId>": { } } } }
```

Money is in USD. Dates are `YYYY-MM-DD`. Week documents are keyed by the Monday of an ISO week.

## Written by the weekly update

| Document | Shape |
|---|---|
| `weeks/{Monday}` | `start`, `end`, `iso`, `pulledAt`, `sources[]`, `notes{}`, `brands.{maia,avia}` with the scorecard fields below. The latest week also carries `creative`, `topAds[]`, `supportReasons[]`. |
| `actuals/daily` | `through`, `latest`, `pulledAt`, `days.{date}` = `revenue, orders, ncOrders, ncRevenue, adSpend, refunds, cogs, shipping, gateway, taxes, bags, bottles`. |
| `strategists/weekly` | `source`, `through`, `rules`, `names`, `weeks.{Monday}` = `iso, start, end, days, rows.{code}, total`; each row is `spend, ncRev, nc, ads, tested, winners, potential, launched`. |
| `cs/weekly` | `pulledAt`, `weeks.{Monday}` = `email, all, admin, reasons, agents[], ai, csat, phone`; `now` (the backlog today); `structure`; `notes[]`; `gaps[]`. |
| `inventory/desk` | Reorder run settings (`asOf`, `cutoff`, `alpha`, `beta`, `growthClip`, `historyWeeks`, `ewmaWeeks`) and `weeks.{Monday}` = `bags, bottles`. |
| `inventory/bom` | `items[]` = `title, bags, bottles, physical`: how each product title converts to physical units. |
| `meta/refresh`, `meta/refresh_cs` | The update logs: `at`, `by`, `week`, `checks[]` = `name, ok, note`. |

Scorecard fields per brand: `revenue, orders, ncOrders, ncRevenue, adSpend, refunds, cogs, shipping, gateway, taxes, sessions, aov, cvr, atcRate, metaSpend, metaCpa, metaRoas, metaCpm, metaCpoc, googleSpend, googleRoas, amazonSales, tickets, ticketsClosed, firstResponseH, avgResponseH, resolutionH, zeroTouch, unauthorized, subContacts, briefsCreated, videosCompleted, staticsDelivered, wipOpen, waitingLaunch, aged14, ltv90`. A missing field shows as "No data".

## Read from the plan

| Document | Shape |
|---|---|
| `plan/model` | `source`, `weeks[]` (`n, iso, start, end, activeFrom, activeTo, activeDays, extra`), `lines.{line}` with weekly arrays `adSpend, ncRoas, ncRevenue, newOrders, rebillOrders, rebillRevenue, revenue, fulfillment`, `total`, `units`, `planPO`, `poValue`, `cash`, `monthly`, `payments[]`, `inputs`, `notes[]`. |

## Edited by the team on the page

| Document | Shape |
|---|---|
| `items/{id}` | `type` = `issue`, `action` (a task), `need` or `decision`; `title, owner, brand, due, note, status, created, week`; tasks also carry `workstream, focus, leverage, rank, cost, doneAt`. |
| `settings/targets` | `{brand}.{kpiId}` = target value. |
| `settings/owners` | `{groupId}` = owner name. |
| `comments/{week}__{brand}` | `{kpiId}` = the owner's one-line note. |
| `inventory/pools` | `pools.{item}` = `name, unit, line, count, countDate, countNote, conf, unitCost, leadDays, safetyDays, reviewDays, inbound[]`; `paid.{paymentId}`. |
| `actuals/cash` | `w{n}.cash` = the bank balance typed in for plan week `n`. |

The weekly update never writes the documents in this last table.

## Formulas computed in the page

- Contribution after ads = revenue − taxes − refunds − product cost − shipping − payment fees − ad spend.
- First-order ROAS = new-customer revenue ÷ ad spend. Cost per new customer = ad spend ÷ new-customer orders.
- Plan to date = the week's plan spread evenly over its plan days.
- Stock on hand = last count + inbound received since the count − units sold since the count.
- Tasks carry over: an open task belongs to the week (or month) of its due date, or of the day it was created; once that period ends it shows in the current one, marked with where it came from.
