Hi Mike,

Thanks for the update, and apologies for the delay getting back to you. Given it's not yet clear how long the data owner/business area review will take, we'd like to proceed now under the standard SDC rules you described, as you offered — happy to revisit if the data owner's eventual ruling turns out to allow something less restrictive.

Project name: rfasta
Project ID: ons-ids-tooling-rfasta-prod
Review bucket: ons-ids-data-rfasta-prod-review

What's changed since the original request: the below-threshold counts you caught were a real bug on our side — suppression was checking the underlying row count as a stand-in for "every published figure in this row is safe," which doesn't actually hold (e.g. refunds can net a count like journeys down near zero even when the row count itself is healthy). That's fixed: every published count column is now checked directly, and the whole row is suppressed together if any one of them is ≤10. On top of that, every value that survives suppression is now rounded to the nearest 5, per the standard rule you described. Both are verified: a check that rebuilds all 8 files from scratch confirms zero rows have an unsuppressed count ≤10, and every surviving value is now a multiple of 5.

Output type: Analytical output (CSV data tables — no graphs, code, or text outputs in this request), same 8 files as the original request.

Files (8), full names, all with the 20261012_ date prefix:

20261012_busyness_OD_DISCLOSURE_SAFE_od_daily.csv
20261012_busyness_OD_DISCLOSURE_SAFE_od_weekly.csv
20261012_busyness_OD_DISCLOSURE_SAFE_od_monthly.csv
20261012_busyness_OD_DISCLOSURE_SAFE_od_yearly.csv
20261012_busyness_indicator_DISCLOSURE_SAFE_weekly.csv
20261012_busyness_indicator_DISCLOSURE_SAFE_monthly.csv
20261012_busyness_indicator_DISCLOSURE_SAFE_indexed_weekly.csv
20261012_busyness_indicator_DISCLOSURE_SAFE_indexed_monthly.csv
Dataset, access restrictions, and variable definitions: unchanged from our original request dated 2026-09-14 — happy to resend that detail in full if it's easier for you than pulling up the earlier thread.

SDC methods applied (updated): Primary cell suppression (any row built from 10 or fewer underlying source transaction rows, or with any published count ≤10, has every measure replaced with "c", flagged via disclosure_status), plus rounding to the nearest 5 for every count/total value that isn't suppressed. Averages/ratios (e.g. avg_journey_miles) and the regional index value are not rounded, since they aren't subject counts themselves — happy to revisit that if you'd prefer otherwise. Still primary suppression only — no secondary/complementary suppression — same open question as last time on whether that's needed for the regional-total tables.

Timeline: [fill in]

Thanks,
Saurabh

