# Technology reference

Every library, format and technique used in this project, what it is used
**for**, and where in the code. Written so any "what did you use for X?"
question can be answered immediately.

**Nothing here is aspirational.** Every entry was verified against the running
code by checking the imports and the call sites.

---

## The short answer

> "Python 3.11 with pandas. Nine pinned libraries, each doing one job. No
> database, no cloud, no API — it reads a spreadsheet and writes files to a
> folder. The dashboard is Streamlit, running locally."

---

## The whole stack, on one page

| Library | Version | Used for | Where |
|---|---|---|---|
| **pandas** | 2.2.3 | all data handling: tables, grouping, joins, time series | everywhere (32 files) |
| **numpy** | 1.26.4 | arithmetic, logs, medians, array maths | everywhere (24 files) |
| **scipy** | 1.13.1 | **two calls only** — the t distribution and the normal | `detect.py` lines 77–79 |
| **statsmodels** | 0.14.4 | STL seasonal decomposition | `condition.py` line 164 |
| **scikit-learn** | 1.5.2 | Isolation Forest (structural anomalies) | `structural.py` line 168 |
| **networkx** | 3.3 | PageRank, Louvain, betweenness, density | `graph.py`, `network.py`, `communities.py` |
| **pyarrow** | 17.0.0 | reading and writing Parquet | via pandas `to_parquet` / `read_parquet` |
| **openpyxl** | 3.1.5 | reading the `.xlsx` workbook | `ingest.py` (via pandas), `audit.py` (directly) |
| **streamlit** | 1.39.0 | the dashboard | `app.py`, `app_pages/*` |
| **plotly** | 5.24.1 | every chart, and the HTML export | `app_pages/*`, `export/report.py` |
| **pytest** | 9.1.1 | the test suite | `tests/*` |

**Python 3.11.4** on the development machine, **3.10–3.12** supported. All
packages have prebuilt wheels for macOS arm64 and Windows x86_64, so there is
**no compiler step** and no platform-specific binary anywhere.

---

## Questions you are likely to be asked

### "Do you use a database?"

**No. None at all.** No DuckDB, no SQLite, no Postgres, no SQL of any kind.
Verified by searching the whole codebase — zero matches.

The data is small enough not to need one: the largest table is 728,000 rows,
which pandas holds in memory comfortably. Everything is **files in a folder**.

**If asked whether you should use one:** the honest answer is that a database
would add an installation dependency and an operational surface for no gain at
this size. If the data grew to firm level — tens of millions of rows — the
calculus would change, and **DuckDB would be the natural first step** because
it reads Parquet directly and needs no server.

### "Do you use Parquet? What for?"

**Yes, but not where people assume.** The important correction first:

> **The dashboard reads CSV, not Parquet.** The only Parquet file it opens is
> the edge store.

| What the app reads | Format | How dtypes are protected |
|---|---|---|
| `series_national.csv`, `alerts.csv`, `breaks.csv`, `structural.csv`, `quality.csv` … | **CSV** | `dtype={"sic2": str, ...}` passed explicitly to `read_csv` |
| `vintages/<date>/sic2.parquet` — the 683,000-row edge table | **Parquet** | carried in the file |

So Parquet does **three** jobs, and only one of them is in the dashboard's
path:

| Use | Where | In the app's path? |
|---|---|---|
| **The edge store** — one snapshot per delivery, for counterparty work | `outputs/vintages/<date>/*.parquet` | **yes** — this is the one |
| **Month-partitioned edges** — read one month without touching the rest | `outputs/edges/level=<x>/month=<y>/edges.parquet` | a Phase 2 hook, not yet read by a view |
| **Dtype-safe companions** — for the tests and for analysing outputs directly | every `outputs/*.parquet` | **no** |

**Why the companions exist at all.** CSV has no types: industry code `"01"`
reads back as the integer `1` and loses its leading zero. That was a real bug.
There are two ways to fix it — state the dtypes on every read, or store a
format that carries them. **The project does both**, because the app can state
its dtypes but a test or an ad-hoc analysis should not have to remember to.

**Why keep CSV at all?** CSV is for people — anyone can open it in Excel. The
CSVs total **28.3 MB**, the Parquet **5.9 MB**: about **five times smaller**
for identical content, because it is columnar and compressed.

**If asked why the app does not just read the Parquet:** it could, and it would
be marginally faster. The CSVs are the human-readable artefact and the app
reads the same files a person would, which means **what you see on screen comes
from a file you can open yourself.** That is worth more than the milliseconds.

### "How did you do the t-test?"

**There is no t-test.** This is worth being precise about, because the word
invites the wrong question.

We use the **t distribution**, but not for a hypothesis test. There is no null
hypothesis, no p-value reported, and no significance claim anywhere.

It is used for a **translation**, in `pipeline/detect.py`:

```python
tail = stats.t.sf(abs(ratio), df=n - 1)      # how rare on a t curve
return np.sign(ratio) * stats.norm.isf(tail) # the same rarity on a normal curve
```

Two scipy calls, and they are **the only scipy used in the entire project**:

| Call | What it does |
|---|---|
| `scipy.stats.t.sf` | survival function of the t distribution — the tail probability |
| `scipy.stats.norm.isf` | inverse survival function of the normal — converts a tail back to a value |

**Why:** the yardstick (the MAD) was estimated from a small number of months,
so the raw ratio overstates how surprising a value is. The t distribution has
fatter tails, which accounts for that. The output is restated on a normal scale
so the three-sigma convention still applies.

**If someone says "so it is a significance test":** no. It is a scale
conversion that keeps the rarity fixed. Severity carries no p-value and the
dashboard says so explicitly.

### "What did you use for the Isolation Forest?"

**scikit-learn**, `sklearn.ensemble.IsolationForest`, in
`pipeline/structural.py`.

```python
IsolationForest(contamination=0.03, random_state=0, n_estimators=300)
```

| Parameter | Value | Why |
|---|---|---|
| `n_estimators` | **300** | enough trees that the average stops moving between runs |
| `contamination` | **0.03** | the expected share of anomalies — sets how long the list is, roughly 2–3 a month |
| `random_state` | **0** | fixed, so the same delivery scores identically twice |

It is fed **nine standardised features** per industry-month, not the raw money.
`decision_function` is negated so higher means stranger, then rescaled between
the 1st and 99th percentile onto 0–100.

**This is the only machine learning in the project.** Everything else is
arithmetic.

### "Why not a neural network / GNN?"

Tested and rejected, for two independent reasons recorded in `BUILD_SPEC.md`
§12.5:

1. **Not enough data.** 88 industries × 90 months = **7,920 observations**.
   Nowhere near enough to train a graph network that generalises rather than
   memorises.
2. **The graph is too dense.** At **78% density** every node's neighbourhood is
   almost the whole graph, so the embeddings collapse toward a common mean and
   the structural signal is averaged away.

**Kept as an option** if firm-level data ever arrives, where node counts reach
the tens of thousands and the density problem disappears.

### "What did you use for seasonal adjustment?"

**statsmodels**, `STL` — Seasonal and Trend decomposition using Loess:

```python
STL(filled, period=12, robust=True).fit()
```

`robust=True` so a few extreme months cannot distort the seasonal pattern.

**Why STL and not X-13ARIMA-SEATS**, which is the ONS standard: X-13 needs a
compiled binary that differs between macOS and Windows. STL is pure Python with
identical results on both platforms. **The tool had to run on a MacBook and a
managed Windows machine from the same zip**, and that ruled X-13 out.

**Worth knowing:** the year-on-year signal does not need seasonal adjustment at
all, because comparing December with December cancels the pattern. STL is used
for the single-month signal only.

### "What did you use for the network analysis?"

**networkx** for all of it:

| Function | Used for |
|---|---|
| `nx.pagerank` | influence, both value-weighted and volume-weighted |
| `nx.betweenness_centrality` | computed and stored, but given no view — 77–83% of industries score exactly zero |
| `nx.density` | the diagnostic published beside every network metric |
| `louvain_communities` | community detection, at SIC-5 |
| `modularity` | the score that says whether the communities mean anything |

All graphs are built through **one function**, `graph.build_graph()`, which is
the only place edge direction is set. PageRank inverts silently if payer and
payee are swapped — no error, just a wrong answer — so there is a golden test
in `tests/test_direction.py` asserting the orientation.

### "How do you read the Excel file?"

**Two different readers, deliberately.**

| | Library | Where |
|---|---|---|
| The pipeline | **pandas** `read_excel` / `ExcelFile` (openpyxl underneath) | `ingest.py` |
| The audit | **openpyxl** directly, `load_workbook(read_only=True)`, row by row | `audit.py` |

**Why two:** the audit exists to catch bugs in the pipeline. If it used the same
reading code it would share the same bugs and agree for the wrong reason. It
has its own reader, its own date parser and **imports nothing from the
pipeline**.

### "Is anything hosted? Any API? Any cloud?"

**No.** It runs entirely on the machine it is installed on.

- no server, no container, no cloud account
- no outbound network calls at runtime
- Streamlit telemetry is **switched off** in the launch scripts
- the only internet needed is `pip install` at setup

The exported briefing is a **single self-contained HTML file** — Plotly charts
are embedded, so they stay interactive with no internet connection.

### "What about the dashboard framework?"

**Streamlit**, chosen over Dash and Flask because the whole thing is Python with
no HTML, CSS or JavaScript to maintain. The charts are **Plotly**, which matters
for one specific reason: **the same figure object renders in the app and
serialises to standalone HTML**, so the export cannot drift from what is on
screen.

Runs on `localhost`, port configurable via `port.txt` because Windows reserves
TCP ranges and can refuse the default.

---

---

## How a number gets from the spreadsheet to the screen

A natural question: are all the values and charts precomputed and simply
fetched, or worked out when you look at them?

**It is a split, and the rule is simple:**

> **Anything that needs history, or is expensive, is precomputed.**
> **Anything that depends on which buttons you pressed is computed live.**

### Precomputed by the pipeline, written to `outputs/`

| | Why it cannot be live |
|---|---|
| **severity** and the three z signals | needs 21+ months of prior history for every industry |
| **confidence** and the "Why" text | needs counterparty decompositions for the top 10 per month |
| **the break register** | scans each whole series for level shifts |
| **structural score** | fits an Isolation Forest over 7,783 rows |
| **PageRank, betweenness, communities** | builds a graph for every month |
| **the panels** (inflow, outflow, PFI, both bases) | aggregates 683,000 edges |

### Computed live, on every control change

| | Measured |
|---|---|
| **every £ change and %** on Movers | a groupby over 8,010 panel rows — sub-millisecond |
| **the counterparty decomposition** on *Why did it move?* | **15-25 ms** for 85 partners |
| **the driver lines** on Movers | three decompositions, **under 50 ms** total |
| **every Plotly chart** | rebuilt from scratch each render |
| **the worked examples** in the method guides | recomputed from `outputs/` so they cannot go stale |
| **the typical-range band** on Trends | percentiles of whichever series is on screen |

### Loading, measured

```
series_national.csv     8,010 rows     82 ms
alerts.csv             32,538 rows    167 ms
vintages/sic2.parquet 682,757 rows    265 ms
```

Then **cached for 300 seconds** by Streamlit's `@st.cache_data`. The cost is
paid once; every control change after that is instant.

### Why the £ changes are not precomputed

Movers *could* store every change for every combination. But that is
**month x measure x basis x level x region** — and the regional dimension alone
multiplies it by 13. Computing it from the panel on demand is a groupby over
8,010 rows.

**So: store what is expensive to derive, derive what is cheap.** Severity needs
two years of history and cannot be rebuilt on a click. A subtraction can.

### One case where the answer changed during the build

**The driver lines on Movers are regenerated live**, even though `alerts.csv`
already contains them.

The stored lines are written for one fixed selection — All-UK, classified,
division level. **The moment you pick a region or switch basis, the stored
sentence describes something you are no longer looking at.** At a few tens of
milliseconds for three, there was no reason to serve a stale one.

**The Overview still uses the stored line**, because that page only ever shows
the default selection. Which is also why there is a test asserting the stored
lines match what the generator currently produces — **they went stale once
already**, when the wording changed after the pipeline had already run.

### The architectural shape, in one line

> "A batch pipeline writes flat files. The dashboard is a reader with a cache
> and a few cheap calculations on top. There is no service, no query engine
> and no state — restart it and nothing is lost."

## Everything the project does NOT use

Worth having ready, because "why didn't you use X" is a common question.

| Not used | Why not |
|---|---|
| **DuckDB / SQL / any database** | 728k rows fits in memory; a database adds dependency and operational surface for no gain |
| **Spark / Dask** | the entire dataset is under 1 GB |
| **X-13ARIMA-SEATS** | needs a platform-specific compiled binary; STL is pure Python and cross-platform |
| **A GNN or any neural network** | 7,920 observations, and 78% graph density collapses the embeddings |
| **Docker** | the target machines are a managed Windows laptop and a MacBook; a venv is simpler and needs no admin rights |
| **Airflow / Prefect** | it is a monthly manual run, not a schedule |
| **A cloud warehouse** | the data is official statistics in development, held locally by choice |
| **SHAP or any explainer** | the structural features are already interpretable — "more arriving from unclassified payers" needs no explaining |

---

## Where the techniques live

| Technique | Library | File |
|---|---|---|
| Median / MAD robust statistics | numpy | `detect.py`, `structural.py` |
| t-distribution rescaling | scipy | `detect.py` |
| STL seasonal decomposition | statsmodels | `condition.py` |
| Binary-segmentation break detection | numpy (hand-written) | `condition.py` |
| CUSUM drift | pandas rolling | `detect.py` |
| Isolation Forest | scikit-learn | `structural.py` |
| PageRank / betweenness / density | networkx | `graph.py`, `network.py` |
| Louvain communities + Jaccard matching | networkx | `communities.py` |
| Herfindahl concentration index | numpy (hand-written) | `structural.py` |
| Three-way change attribution | pandas | `decompose.py` |

**Note what is hand-written rather than imported:** the break detector, the
Herfindahl index and the change decomposition. Each is a few lines of
arithmetic, and writing them means the reasoning is visible and testable
rather than hidden in a dependency.

---

## The numbers, if asked about scale

| | |
|---|---|
| Source workbook | ~37 MB `.xlsx`, 728,732 rows |
| Regional file | ~317 MB `.csv` |
| SIC-5 file (optional) | ~820 MB `.csv`, streamed not loaded |
| Output CSVs | 28.3 MB across 22 files |
| Output Parquet | 5.9 MB across 14 files |
| Code | ~9,400 lines |
| Tests | 665, all passing |
| Audit checks | 42, reconciling outputs to the raw file |
| Full rebuild | about 20 minutes |
| Quick run from cache | under a minute |

---

## If you only remember four things

1. **Pandas and nine pinned libraries. No database, no cloud, no API.** It
   reads a spreadsheet and writes files to a folder.
2. **There is no t-test.** The t distribution is used for a scale conversion,
   and nothing in the tool reports a p-value.
3. **The only machine learning is the Isolation Forest.** Everything else is
   arithmetic you can check by hand.
4. **A batch pipeline writes flat files; the dashboard reads them.** Expensive
   things that need history are precomputed; anything that depends on your
   control selections is worked out live, in milliseconds.
