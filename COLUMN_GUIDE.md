# GB Rail Busyness Indicator — Column Guide

**What this document is for:** every column that appears anywhere in the published
dataset (the Excel workbook, and the charts built from it), explained three ways for
each one — where the number comes from, exactly how it's calculated, and a small,
hand-workable example you can check with a calculator. If a chart or a cell in the
spreadsheet doesn't make sense, this is the document that should settle it.

No knowledge of databases, GCP, or the pipeline code is assumed anywhere below.

---

## 1. Start here: one example, used for the rest of this document

Rather than invent a new example for every column, this section sets up **one small,
fictional scenario** and the rest of the document keeps coming back to it. The numbers
are made up but the arithmetic is exactly how the real pipeline works.

### 1.1 Why season tickets produce decimal journey counts at all

Single and return tickets are easy: a single ticket is 1 journey, a return is 2. A
**season ticket** is different — it lets the holder travel as many times as they
like within its validity period, and the system doesn't log every individual tap-in
against it the way it would a single ticket. So instead of a real count, the
transaction carries a **journey weighting**: a number meant to represent how many
journeys that season ticket is likely to be worth over its validity, set once at the
point of sale. ONS's own published definition for this figure confirms it's
calculated differently for season tickets specifically — *"for season tickets, the
Season Ticket Journey Weightings"* — but **the exact formula the rail industry uses
to set that weighting isn't something this project has had sight of**, so rather than
invent a precise-looking "official" calculation and present it as confirmed, here's
a clearly-labelled illustration of the *kind* of arithmetic that produces a number
like this, so the shape of it makes sense even without the real formula:

> Suppose a season ticket is valid for 20 working days, and the assumption is 2
> single journeys per working day (one each way). A theoretical maximum would be
> `20 × 2 = 40` journeys. But real commuters don't travel on 100% of their valid
> days — annual leave, sick days, occasional working from home — so the weighting
> applies a usage rate below 100% to that theoretical maximum. If that rate were,
> illustratively, 91.25%: `40 × 0.9125 = 36.5`. **That 91.25% is not a real,
> confirmed industry figure — it's chosen here purely to land on a believable
> decimal.** The real mechanism is the same shape (a maximum, scaled down by a
> usage rate that's essentially never a round number) even though the real rate
> isn't published anywhere this project has seen.

**This is also exactly why a partial refund of a season ticket produces a decimal.**
If a season-ticket holder returns their ticket early for a refund, the refund is
prorated to the unused portion of the validity period — and that proration is
applied to the *weighted journey figure* in exactly the same way it's applied to the
pound value refunded, since both exist to answer "how much of what was paid for
actually went unused."

### 1.2 The worked example used for the rest of this document

**Imagine 5 real-world ticket transactions, all for journeys ending in the "South
West" region, all happening in March 2026:**

| # | What happened | Journeys this represents | Total miles for those journeys |
|---|---|---|---|
| A | A single one-way ticket, a 45-mile leisure trip | 1.0 | 45.0 |
| B | A return ticket, commuting 25 miles each way | 2.0 | 50.0 |
| C | A season ticket, weighted as 36.5 commuting journeys of 20 miles each over the month (the illustration in §1.1) | **36.5** | 730.0 |
| D | **A refund** of a *different*, smaller season ticket — full weighting 8.5 journeys (5 valid days, same kind of calculation as §1.1), returned after 2 of its 5 days were used, so 3/5 of it is refunded: `8.5 × 3/5 = 5.1` journeys, at the same 20 miles/journey | **−5.1** | −102.0 |
| E | A ticket covering 3 journeys of 60 miles each (a group or multi-use ticket) | 3.0 | 180.0 |

A few things worth noticing about this table before we calculate anything:

- **A refund is a negative row, not a deletion.** Row D doesn't erase an earlier row —
  it's its own row, with negative journeys and negative miles, that cancels out what
  an earlier sale added. This is how refunds work everywhere in this dataset. A
  *partial* refund (row D) works exactly the same way, just scaled to the unused
  fraction rather than the whole ticket.
- **"Journeys" and "tickets" are not the same thing.** Row C is *one* ticket (a
  season ticket) but represents *36.5* journeys. This distinction matters a lot below.
- **Journeys are very often NOT whole numbers — this is normal, not a data error.**
  Single and return tickets almost always give a whole number (1, or 2), but
  anything involving a season ticket's weighting — a sale or a refund of one — can
  land on a decimal, for the reason in §1.1. **If you open the real published Excel
  file and see `net_passenger_journeys` showing something like `1,847,213.75`, that's
  expected, not a formatting glitch.** Only `net_tickets` and `row_count` are
  guaranteed whole numbers; every journey-based column can carry decimals.
- Every number in the "Total miles" column is already the **full distance for every
  journey that row represents** — row C's 730 miles is 36.5 journeys × 20 miles each,
  already multiplied together. It is *not* a single journey's distance. This is the
  single most important thing to get right, and the one thing people most often get
  wrong when reading this dataset — see §3.4 below for exactly why.

These 5 rows are everything the rest of this document calculates from.

---

## 2. The two shapes the data comes in

Every file in the published dataset is one of two shapes:

- **Destination-only**: one row per *time period* and *destination region* — "how
  many journeys ended in the South West in March 2026," regardless of where they
  started.
- **Origin-destination**: one row per *time period*, *origin region*, **and**
  *destination region* — "how many journeys went from London to the South West in
  March 2026" specifically.

Both shapes are built from exactly the same underlying ticket transactions, just
grouped differently. Everything in §3 applies to both; §4 covers the handful of
columns that only exist in one shape or the other.

---

## 3. Every column, explained

### 3.1 The columns that identify a row

| Column | Appears in | What it is |
|---|---|---|
| `destination_region_code`, `destination_region_name` | all files | The region a journey **ended** in. Code is the official short code (e.g. `E12000009`); name is the readable version (e.g. "South West"). |
| `origin_region_code`, `origin_region_name` | origin-destination files only | The region a journey **started** in — same code/name system. |
| `month`, `iso_week`, `travel_date`, `year` | one of these per file | The time period that row covers (see §3.6). |

**"Unknown region"** appears as a value in these columns, not an error — it means the
source data didn't record a usable region for that end of the journey. It's kept as
its own row rather than dropped, so volume never silently disappears; see the
published methodology report for how common this is and when it started appearing.

### 3.2 `net_passenger_journeys` — how many journeys happened

**Where it comes from:** every ticket transaction records how many journeys it
represents (not how many tickets — see §3.3). Refunds record this as a *negative*
number. This column is simply all of those added together for the region and period
the row covers.

**The calculation:** `SUM(journeys across every transaction in this region/period)`.

**Worked example**, using the 5 rows in §1 — this *is* the row for South West, March
2026, so we add up the "Journeys this represents" column:

```
   1.0   (row A)
+  2.0   (row B)
+ 36.5   (row C)
+ (−5.1) (row D, the refund)
+  3.0   (row E)
--------
= 37.4
```

**`net_passenger_journeys` for this row is 37.4.** "Net" means net of refunds —
nothing more exotic than that; the fractional result is simply what happens when you
add whole-number journeys (rows A, B, E) to fractional, weighted ones (rows C, D).
The refund in row D genuinely reduced the total; it isn't hidden or treated
specially.

### 3.3 `net_tickets` — how many tickets were sold

**Where it comes from:** a count of the ticket transactions themselves (sales minus
refunds), not the journeys they represent.

**The calculation:** `SUM(+1 per sale, −1 per refund)` for the region and period.

**Worked example:** rows A, B, C, and E are each one ticket sold (+1 each); row D is
one refund (−1).

```
1 + 1 + 1 − 1 + 1 = 3
```

**`net_tickets` for this row is 3.** Unlike `net_passenger_journeys`, this column is
always a whole number — a ticket is either sold or refunded, there's no such thing as
a fractional sale.

**Why this differs from `net_passenger_journeys` (37.4):** one season ticket (row C)
is a *single* ticket but represents *36.5* journeys. This is the entire reason both
columns exist side by side — `net_tickets` answers "how many purchases," while
`net_passenger_journeys` answers "how much actual travel." A season ticket holder
who travels every weekday moves these two numbers very far apart; a single-trip
leisure traveller barely moves them apart at all. If the two columns ever start
tracking each other unusually closely or diverging unusually sharply for a region,
that's a real shift in the mix of ticket types being sold there, not a data error.

### 3.4 `total_passenger_miles` — the headline distance figure

**Where it comes from:** each ticket transaction already records the *total* distance
it represents — the distance of the route multiplied by however many journeys that
transaction covers. **This multiplication has already been done upstream, by the
source system, before this dataset ever sees it.** This column just adds that
already-multiplied figure across every transaction in the region/period.

**The calculation:** `SUM(total miles across every transaction in this region/period)`
— i.e., exactly the "Total miles" column in §1, added up.

**Worked example:**

```
  45.0   (row A)
+ 50.0   (row B)
+ 730.0  (row C)
+ (−102.0) (row D, the refund)
+ 180.0  (row E)
--------
= 903.0
```

**`total_passenger_miles` for this row is 903.0.**

**The single most important gotcha in this whole dataset:** because this figure is
*already* journeys × distance, it must **never be multiplied by `net_passenger_journeys`
again** to get a "total distance." Doing that accidentally happened once during this
project's development and inflated average journey length figures by orders of
magnitude (250+ miles instead of the correct ~25-30) — entirely because a number that
was already a total got treated as if it were a per-journey figure and multiplied a
second time. If you're ever building your own calculation from this column, the rule
is: **divide it, never multiply it, to get to a per-journey figure.** That's exactly
what the next two columns do.

### 3.5 The two average-distance columns

There are two different, both legitimate, ways to describe "how far did people
travel" — and the dataset deliberately keeps them separate because they answer
different questions. Both exist in the destination-only files under one set of names,
and in the origin-destination files under a clearer set of names:

| Destination-only file name | Origin-destination file name | Question it answers |
|---|---|---|
| `avg_journey_miles_weighted` | `avg_journey_miles` | How far does a typical **journey** go? |
| `avg_journey_miles_unweighted` | `avg_passenger_miles_per_ticket` | How many miles does a typical **ticket sold** represent? |

(The `_weighted`/`_unweighted` names in the destination-only files are a historical
naming artifact from earlier in this project and are **not** a reliable guide to what
they mean — use the table above, not the column name, to know which is which.)

#### `avg_journey_miles_weighted` / `avg_journey_miles` — average journey length

**The calculation:** `total_passenger_miles ÷ net_passenger_journeys`.

**Worked example:** `903.0 ÷ 37.4 = 24.14` miles (rounded to 2 decimal places — this
division doesn't come out to a clean number, which is normal for this column once
any fractional journey weighting is involved).

**This is the headline "average journey length" figure.** It answers: if you picked
one random journey out of everyone who travelled, how far did it go, on average?
A season ticket holder's 36.5 weighted commuting journeys count 36.5 times over in
this calculation — exactly as they should, since that's how much real travel the
weighting represents.

#### `avg_journey_miles_unweighted` / `avg_passenger_miles_per_ticket` — passenger-miles per ticket sold

**The calculation:** `total_passenger_miles ÷ row_count` (see §4.1 for what
`row_count` is — in this example it's 5, the number of transaction rows).

**Worked example:** `903.0 ÷ 5 = 180.6` passenger-miles per ticket row.

**This answers a different question**: of the tickets sold, how many passenger-miles
does a typical one represent? A season ticket (row C, 730 miles across a 36.5-journey
weighting) counts as *one* ticket here, the same weight as a single one-way leisure
ticket (row A, 45 miles) — which is why this number (180.6) is so much larger than
the ~24-mile "average journey length" above would suggest: it's being pulled up by
season tickets that pack a large number of passenger-miles into one sold "ticket" row.

**Neither of these is more "correct" than the other — they're genuinely different
questions, which is why both are published rather than one being picked for you.**

### 3.6 The commute-like / leisure-like split

**Where it comes from:** every individual transaction's own distance **per journey**
(not its total passenger-miles — see the gotcha in §3.4) is compared against a single
threshold, currently **30 miles**. A journey at or under 30 miles is "commute-like";
over 30 miles is "leisure-like." This is a provisional, distance-only rule — it has no
way to know someone's actual reason for travelling, and is explicitly labelled
provisional in the methodology report for that reason.

**The calculation, per transaction row:** miles-per-journey = that row's total miles
÷ that row's journeys. If miles-per-journey ≤ 30, that row's journeys count toward
`commute_like_journeys`; otherwise they count toward `leisure_like_journeys`.

**Worked example** — checking each of the 5 rows individually:

| Row | Total miles ÷ journeys | Miles per journey | Classification | Journeys counted |
|---|---|---|---|---|
| A | 45.0 ÷ 1.0 | 45 | Leisure (> 30) | 1.0 |
| B | 50.0 ÷ 2.0 | 25 | Commute (≤ 30) | 2.0 |
| C | 730.0 ÷ 36.5 | 20 | Commute (≤ 30) | 36.5 |
| D (refund) | −102.0 ÷ −5.1 | 20 | Commute (≤ 30) | −5.1 |
| E | 180.0 ÷ 3.0 | 60 | Leisure (> 30) | 3.0 |

```
commute_like_journeys = 2.0 + 36.5 + (−5.1)   = 33.4
leisure_like_journeys = 1.0 + 3.0             = 4.0
```

**Check your work:** these two columns must always add up to
`net_passenger_journeys` — and they do: `33.4 + 4.0 = 37.4`. ✓. This is a genuinely
useful sanity check if you're ever unsure whether a calculation on this data is
right: the commute and leisure columns are a true split of the journeys total,
nothing is lost or double-counted between them, fractional weightings included.

Notice row D, the refund: its own per-journey rate (20 miles) puts it on the
**commute** side this time (it's refunding part of a season ticket, not a leisure
trip), and because its journey count is negative, it correctly *subtracts* from the
commute total rather than the leisure total — exactly undoing whatever original
commute-like sale it's refunding. This is why the split is computed row-by-row and
then summed, rather than computed once from the region's already-summed totals: each
row's own rate decides where it belongs, refunds included.

### 3.7 `total_ticket_miles_unweighted` (destination-only files only)

A secondary distance total, included purely so a reader can cross-check
`total_passenger_miles` against a second, independently-tracked figure from the
source system. If the two ever disagree substantially for the same row, that's worth
investigating; day-to-day, you can treat `total_passenger_miles` as the primary
figure and this one as a consistency check in the background.

---

## 4. Columns that only exist in one file or the other

### 4.1 `row_count`, `low_count_flag`, `disclosure_status` — how many real records, and whether this row is safe to publish

**Where it comes from:** `row_count` is simply a count of the underlying transaction
*rows* behind this published row — not journeys, not tickets, just "how many lines of
raw data did we start from." In our example: rows A, B, C, D, and E — that's **5**.

**Why it exists:** official statistics are never published from a handful of
underlying records, because a very small number of real people or transactions could
potentially be identified or reverse-engineered from the published figures. The rule
used here: **if `row_count` is 10 or fewer, or if any of the published counts
(`net_passenger_journeys`, `net_tickets`, `commute_like_journeys`,
`leisure_like_journeys`) is a small nonzero number — 10 or fewer in size — every
figure in that row is hidden**, replaced with the letter `"c"`, and `low_count_flag`
is set to `True` with `disclosure_status` explaining why in plain text.

**Worked example, continued from §1-3.6:** this exact row has `row_count = 5`. Under
the real rule, 5 ≤ 10, so **this row would be suppressed in the actual published
file** — every value you see calculated above (`37.4`, `3`, `903.0`, `24.14`,
`180.6`, `33.4`, `4.0`) would appear as `"c"` instead, with `disclosure_status`
reading something like *"Suppressed (underlying rows <= 10)."* This example was
deliberately kept small enough to calculate by hand — which happens to also be small
enough that it's exactly the kind of row this rule exists to protect. In the real
dataset, a destination region in a given month is built from many thousands of
transactions, so this situation is the exception, not the rule — but it does happen
at finer grain (a single day, or one specific origin-destination pair), which is
exactly why the rule is applied uniformly everywhere rather than only to the
"obviously small" cases.

Worth noting: this row would actually be caught **twice** over by the full rule —
`row_count = 5` is one trigger, but `leisure_like_journeys = 4.0` is *also* a small
nonzero published count (≤ 10) in its own right, which would trigger suppression of
the whole row even if `row_count` had somehow been large. The ≤10 check applies to
the actual value shown, decimals included — `4.0` counts as "4 or fewer," not as
"technically not a whole 4."

**A second, separate protection — rounding:** any figure that survives the check
above (i.e., isn't replaced with `"c"`) is additionally rounded to the nearest 5
before publication. So even a safely-large number like a real `net_passenger_journeys`
of 1,847,213 would appear as 1,847,215 in the published file — never the exact
original figure. This protects every published number, not just the small ones; see
the methodology report for why both protections exist together rather than one alone.

### 4.2 `is_within_region` (origin-destination files only)

**The calculation:** simply `origin_region_code == destination_region_code` — true if
a journey started and ended in the same region, false otherwise.

**Worked example:** a journey from "South West" to "South West" → `True` (someone
travelling within their own region). A journey from "London" to "South West" →
`False` (a genuine cross-region journey). This is what lets a reader separate
"how much travel stays local" from "how much travel crosses region boundaries"
without needing to compare the origin and destination columns by eye every time.

### 4.3 `journeys_index` (indexed files only)

**Where it comes from:** for each region, one specific time period is fixed as that
region's own "base period," worth exactly 100. Every other period for that SAME
region is then expressed as a percentage of that region's own base-period value.

**The calculation:** `100 × (this period's net_passenger_journeys for Region X) ÷
(the base period's net_passenger_journeys for that SAME Region X)`.

**Worked example:** suppose South West's `net_passenger_journeys` in the base period
(say, January 2023) was 1,000,000, and in March 2026 it's 1,200,000:

```
journeys_index = 100 × 1,200,000 ÷ 1,000,000 = 120
```

**South West's index for March 2026 is 120** — meaning 20% more journeys than its
own base period.

**The gotcha that matters most here:** suppose London's index for the same month is
also 120. **This does not mean London and South West had the same number of
journeys** — it means both regions grew by the same *percentage* relative to their
own, completely separate, starting points. London's base period might have been
10,000,000 journeys and South West's might have been 1,000,000 — a 120 index on both
says nothing about which region is actually busier in absolute terms. **Never compare
index values across regions as if they were on the same scale** — use the
non-indexed files (§3.2) for absolute comparisons, and use the index only to compare
a single region against its own past.

### 4.4 The time period columns

| Column | Format | Covers |
|---|---|---|
| `travel_date` | `YYYY-MM-DD` | One calendar day |
| `iso_week` | `YYYY-Www` (e.g. `2026-W09`) | One ISO calendar week |
| `month` | `YYYY-MM` | One calendar month |
| `year` | `YYYY` | One calendar year |

Every column in §3 is computed completely independently at whichever grain the file
is published at — a monthly row is never built by averaging four weekly rows
together; it's built fresh from the same underlying transactions, just grouped by
month instead of by week. This matters because averaging already-computed averages
(rather than recomputing from the underlying totals) is a common and genuinely easy
mistake to make, and would give a subtly wrong answer whenever the underlying weeks
don't all have exactly the same volume — which they never do.

---

## 5. Quick lookup table

| Column | Section |
|---|---|
| `destination_region_code` / `_name` | §3.1 |
| `origin_region_code` / `_name` | §3.1 |
| `month` / `iso_week` / `travel_date` / `year` | §4.4 |
| `net_passenger_journeys` | §3.2 |
| `net_tickets` | §3.3 |
| `total_passenger_miles` | §3.4 |
| `total_ticket_miles_unweighted` | §3.7 |
| `avg_journey_miles_weighted` / `avg_journey_miles` | §3.5 |
| `avg_journey_miles_unweighted` / `avg_passenger_miles_per_ticket` | §3.5 |
| `commute_like_journeys` | §3.6 |
| `leisure_like_journeys` | §3.6 |
| `is_within_region` | §4.2 |
| `journeys_index` | §4.3 |
| `row_count` | §4.1 |
| `low_count_flag` | §4.1 |
| `disclosure_status` | §4.1 |
| `"c"` (a value you'll see in cells, not a column) | §4.1 |
