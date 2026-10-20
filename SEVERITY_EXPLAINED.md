# How the detectors work, explained with five industries

**Part 1** severity · **Part 2** confidence · **Part 3** the structural detector · **Part 4** how they combine and what reaches the screen

Five industries, **A** to **E**. Three years of monthly PFI. **A is the one we
are testing.**

**Every number here reconciles by hand.** The figures printed in the tables
ARE the figures the arithmetic uses - they are rounded to four decimal places
first, then everything is computed from the rounded values. An earlier draft
printed rounded numbers but calculated from unrounded ones, so four rows did
not add up when checked. If any line here fails to reconcile, that is a bug in
this document.

**Every number here is also the number the tool produces.** The calculation below
is done in the same units as the code, so if you recompute anything from the
dashboard you will get the same answer. An earlier draft of this document used
percentages because they read more easily — that gave 80.6 where the tool gives
79.4, which is exactly the sort of two-versions-of-one-number problem this
project exists to avoid.

**Terms used.** Only three:

| Term | Means |
|---|---|
| **log change** | the change against the same month last year, in log units |
| **median** | the middle value when you sort them |
| **A − median** | A's log change minus the middle industry's log change |
| **usual variation** | how much "A − median" normally moves about |

---

# Part 1 — Severity

## The one sentence

> **Severity does not measure how big a move is. It measures how far the move
> is from what is normal for that industry.**

---

## Table 1 — the raw data

PFI in £m. Nothing calculated.

Three things were built into this data on purpose:

- **June 2025** — *every* industry jumps 40%
- **October 2025** — **only A** jumps 20%
- **January 2025** — **E steps up 60%** and stays there

| Month | A | B | C | D | E |
|---|---|---|---|---|---|
| Jan 2023 | **1005** | 980 | 990 | 1010 | 990 |
| Feb 2023 | **990** | 850 | 1005 | 985 | 995 |
| Mar 2023 | **1010** | 850 | 1000 | 1005 | 995 |
| Apr 2023 | **1010** | 1115 | 1005 | 1000 | 1000 |
| May 2023 | **980** | 1135 | 995 | 995 | 1010 |
| Jun 2023 | **985** | 1100 | 1000 | 985 | 1000 |
| Jul 2023 | **1000** | 880 | 1005 | 1000 | 1000 |
| Aug 2023 | **995** | 1040 | 995 | 995 | 990 |
| Sep 2023 | **1000** | 1020 | 1005 | 1000 | 985 |
| Oct 2023 | **990** | 1040 | 995 | 1000 | 995 |
| Nov 2023 | **1010** | 1155 | 995 | 1015 | 1000 |
| Dec 2023 | **1010** | 1040 | 995 | 1000 | 1020 |
| Jan 2024 | **1030** | 1190 | 1085 | 1050 | 1060 |
| Feb 2024 | **1040** | 1075 | 1105 | 1060 | 1070 |
| Mar 2024 | **1035** | 1115 | 1095 | 1060 | 1055 |
| Apr 2024 | **1020** | 1180 | 1100 | 1075 | 1045 |
| May 2024 | **1035** | 780 | 1105 | 1070 | 1050 |
| Jun 2024 | **1020** | 1000 | 1105 | 1065 | 1050 |
| Jul 2024 | **1040** | 970 | 1105 | 1075 | 1085 |
| Aug 2024 | **1030** | 940 | 1100 | 1045 | 1050 |
| Sep 2024 | **1030** | 1010 | 1095 | 1055 | 1070 |
| Oct 2024 | **1025** | 1345 | 1100 | 1050 | 1050 |
| Nov 2024 | **1045** | 895 | 1080 | 1055 | 1070 |
| Dec 2024 | **1030** | 1245 | 1085 | 1045 | 1065 |
| Jan 2025 | **1055** | 785 | 1195 | 1130 | 1795 |
| Feb 2025 | **1055** | 1055 | 1200 | 1120 | 1795 |
| Mar 2025 | **1065** | 1155 | 1215 | 1105 | 1785 |
| Apr 2025 | **1065** | 1240 | 1200 | 1110 | 1805 |
| May 2025 | **1065** | 1265 | 1205 | 1125 | 1790 |
| Jun 2025 | **1490** | 1800 | 1715 | 1585 | 2485 |
| Jul 2025 | **1085** | 1055 | 1205 | 1145 | 1775 |
| Aug 2025 | **1055** | 1030 | 1220 | 1155 | 1800 |
| Sep 2025 | **1055** | 1295 | 1200 | 1130 | 1825 |
| Oct 2025 | **1265** | 1085 | 1210 | 1110 | 1800 |
| Nov 2025 | **1065** | 865 | 1200 | 1100 | 1795 |
| Dec 2025 | **1075** | 895 | 1205 | 1125 | 1805 |

| | Behaviour | Why it is here |
|---|---|---|
| **A** | calm, grows ~3% a year | **the target** |
| **B** | grows ~6% a year, swings wildly | to show the same move can score low |
| **C** | grows 10% a year, steadily | steady growth must not score |
| **D** | grows ~6% a year | holds the median still |
| **E** | ~6% a year, then +60% step | an extreme industry must not drag the rest |

---

## Table 2 — change against the same month last year

### How one cell is built

Take **A in October 2025**. From Table 1:

```
A, October 2025   =  1265
A, October 2024   =  1025        <- twelve rows higher up

1265 / 1025       =  1.2341      <- the ratio
ln(1.2341)        =  0.2104      <- the log change
```

**0.2104 is the A column, October 2025 row, in Table 2.** Repeat for all five
industries, every month. The first twelve months are blank: no "last year" yet.

### Why the log, and not a percentage

This is the question everyone asks, so answer it head on.

In percentages, **a rise and the equivalent fall are not the same size**:

| What happens | As a % | As a log |
|---|---|---|
| doubles | +100% | **+0.6931** |
| halves back again | −50% | **−0.6931** |

Doubling then halving puts you exactly where you started. In logs that is
obvious — **+0.6931 and −0.6931 cancel**. In percentages, +100 and −50 look
like completely different sized events.

**Why that matters here.** Everything that follows measures *distances* — how
far this month is from normal. If the units themselves are lopsided, then a
rise is always further from zero than the equivalent fall, and **the detector
would systematically favour spotting rises over collapses.** The log removes
that bias.

A rough reading guide: for small moves the log is close to the percentage
divided by 100 (0.0290 is about +2.9%). It only pulls away for large moves, and
large moves are exactly where it is needed.

The last column of Table 2 shows A's percentage alongside, **for orientation
only** — the arithmetic uses the log.

### How the median column is built

Sort the five log changes and take the **third**. No formula — it is the middle.

**October 2025**, sorted lowest to highest:

```
B = -0.2148    D = +0.0556    C = +0.0953    A = +0.2104    E = +0.5390
                              ^^^^^^^^^^^^
                              the middle one
```

Median = **+0.0953**, and it is **C**. The *Middle* column in Table 2 names
which industry it was each month, so you can check any row.

```
A − median  =  0.2104 − 0.0953  =  +0.1151
```

| Month | A | B | C | D | E | Middle | MEDIAN | **A − median** |
|---|---|---|---|---|---|---|---|---|
| Jan 2024 | **+0.0246** | +0.1942 | +0.0916 | +0.0388 | +0.0683 | E | +0.0683 | **-0.0437** |
| Feb 2024 | **+0.0493** | +0.2348 | +0.0949 | +0.0734 | +0.0727 | D | +0.0734 | **-0.0241** |
| Mar 2024 | **+0.0245** | +0.2714 | +0.0908 | +0.0533 | +0.0586 | E | +0.0586 | **-0.0341** |
| Apr 2024 | **+0.0099** | +0.0567 | +0.0903 | +0.0723 | +0.0440 | B | +0.0567 | **-0.0468** |
| May 2024 | **+0.0546** | -0.3751 | +0.1049 | +0.0727 | +0.0388 | A | +0.0546 | **+0.0000** |
| Jun 2024 | **+0.0349** | -0.0953 | +0.0998 | +0.0781 | +0.0488 | E | +0.0488 | **-0.0139** |
| Jul 2024 | **+0.0392** | +0.0974 | +0.0949 | +0.0723 | +0.0816 | E | +0.0816 | **-0.0424** |
| Aug 2024 | **+0.0346** | -0.1011 | +0.1003 | +0.0490 | +0.0588 | D | +0.0490 | **-0.0144** |
| Sep 2024 | **+0.0296** | -0.0099 | +0.0858 | +0.0535 | +0.0828 | D | +0.0535 | **-0.0239** |
| Oct 2024 | **+0.0347** | +0.2572 | +0.1003 | +0.0488 | +0.0538 | E | +0.0538 | **-0.0191** |
| Nov 2024 | **+0.0341** | -0.2550 | +0.0820 | +0.0387 | +0.0677 | D | +0.0387 | **-0.0046** |
| Dec 2024 | **+0.0196** | +0.1799 | +0.0866 | +0.0440 | +0.0432 | D | +0.0440 | **-0.0244** |
| Jan 2025 | **+0.0240** | -0.4160 | +0.0966 | +0.0734 | +0.5267 | D | +0.0734 | **-0.0494** |
| Feb 2025 | **+0.0143** | -0.0188 | +0.0825 | +0.0551 | +0.5173 | D | +0.0551 | **-0.0408** |
| Mar 2025 | **+0.0286** | +0.0352 | +0.1040 | +0.0416 | +0.5259 | D | +0.0416 | **-0.0130** |
| Apr 2025 | **+0.0432** | +0.0496 | +0.0870 | +0.0320 | +0.5465 | B | +0.0496 | **-0.0064** |
| May 2025 | **+0.0286** | +0.4835 | +0.0866 | +0.0501 | +0.5334 | C | +0.0866 | **-0.0580** |
| Jun 2025 | **+0.3790** | +0.5878 | +0.4396 | +0.3976 | +0.8615 | C | +0.4396 | **-0.0606** |
| Jul 2025 | **+0.0424** | +0.0840 | +0.0866 | +0.0631 | +0.4922 | B | +0.0840 | **-0.0416** |
| Aug 2025 | **+0.0240** | +0.0914 | +0.1035 | +0.1001 | +0.5390 | D | +0.1001 | **-0.0761** |
| Sep 2025 | **+0.0240** | +0.2486 | +0.0916 | +0.0687 | +0.5339 | C | +0.0916 | **-0.0676** |
| Oct 2025 | **+0.2104** | -0.2148 | +0.0953 | +0.0556 | +0.5390 | C | +0.0953 | **+0.1151** |
| Nov 2025 | **+0.0190** | -0.0341 | +0.1054 | +0.0418 | +0.5173 | D | +0.0418 | **-0.0228** |
| Dec 2025 | **+0.0428** | -0.3301 | +0.1049 | +0.0738 | +0.5276 | D | +0.0738 | **-0.0310** |

---

## Read Table 2 and you have the answer already

Look down the **A − median** column.

**It sits around −0.03 or −0.04 every month.** A grows a little slower than
the middle of the pack, consistently.

**In October 2025 it is +0.1151.**

That is the finding. Not that A rose 23.4% — that **A beat the middle industry
by 0.115 in log terms when it normally trails it by about 0.034.**

---

## Table 3 — A's history, which is Table 2's "A − median" column

To judge whether +0.1151 is unusual we need A's earlier values: the **21
months before October 2025**, copied straight out of Table 2.

| Month | A − median | distance from −0.0341 |
|---|---|---|
| Jan 2024 | -0.0437 | 0.0096 |
| Feb 2024 | -0.0241 | 0.0100 |
| Mar 2024 | -0.0341 | 0.0000 |
| Apr 2024 | -0.0468 | 0.0127 |
| May 2024 | +0.0000 | 0.0341 |
| Jun 2024 | -0.0139 | 0.0202 |
| Jul 2024 | -0.0424 | 0.0083 |
| Aug 2024 | -0.0144 | 0.0197 |
| Sep 2024 | -0.0239 | 0.0102 |
| Oct 2024 | -0.0191 | 0.0150 |
| Nov 2024 | -0.0046 | 0.0295 |
| Dec 2024 | -0.0244 | 0.0097 |
| Jan 2025 | -0.0494 | 0.0153 |
| Feb 2025 | -0.0408 | 0.0067 |
| Mar 2025 | -0.0130 | 0.0211 |
| Apr 2025 | -0.0064 | 0.0277 |
| May 2025 | -0.0580 | 0.0239 |
| Jun 2025 | -0.0606 | 0.0265 |
| Jul 2025 | -0.0416 | 0.0075 |
| Aug 2025 | -0.0761 | 0.0420 |
| Sep 2025 | -0.0676 | 0.0335 |

**Only months before October 2025.** October itself is excluded — a month
cannot help decide what counts as normal for itself.

---

## The calculation

### Step 1 — what is normal for A

Sort those 21 numbers, take the middle:

```
-0.0761 -0.0676 -0.0606 -0.0580 -0.0494 -0.0468 -0.0437 -0.0424 -0.0416 -0.0408 -0.0341 -0.0244 -0.0241 -0.0239 -0.0191 -0.0144 -0.0139 -0.0130 -0.0064 -0.0046 +0.0000
```

**A's normal is −0.0341.**

### Step 2 — how much A normally varies

We know A's normal is **−0.0341**. Now we need to know how far A's gap
*usually sits from that normal*, so we can judge whether +0.1151 is a lot
**for A**.

#### 2a. How far is each month from the normal?

Take each of the 21 gaps and measure its distance from −0.0341, **ignoring
whether it is above or below**. That is the right-hand column of Table 3.

Three examples:

```
Jan 2024:   | -0.0437 - (-0.0341) |  =  0.0096
Mar 2024:   | -0.0341 - (-0.0341) |  =  0.0000     <- sits exactly on the normal
May 2024:   | +0.0000 - (-0.0341) |  =  0.0341     <- the furthest above
```

Signs are dropped because we want **distance**. A month 0.01 below the normal
and a month 0.01 above it are equally far from it.

#### 2b. Take the middle of those distances

Sort the 21 distances and count to the middle, exactly as we did for the
median:

```
 1. 0.0000       8. 0.0102      15. 0.0239
 2. 0.0067       9. 0.0127      16. 0.0265
 3. 0.0075      10. 0.0150      17. 0.0277
 4. 0.0083      11. 0.0153  <-  18. 0.0295
 5. 0.0096      12. 0.0197      19. 0.0335
 6. 0.0097      13. 0.0202      20. 0.0341
 7. 0.0100      14. 0.0211      21. 0.0420
```

**The 11th is 0.0153.** Ten distances are smaller, ten are larger.

**That number is the MAD.**

#### What MAD means, and why we use it

**MAD stands for Median Absolute Deviation.** Read the name backwards and it
is the recipe:

| | |
|---|---|
| **Deviation** | how far each month is from the normal |
| **Absolute** | ignore the sign, we only want distance |
| **Median** | take the middle of those distances |

So the MAD is **"the typical distance from normal"** — half the months are
closer than it, half are further.

**Why we need such a thing at all.** +0.1151 means nothing on its own. It is
only large *relative to how much A normally moves about*. The MAD is what
turns "it moved 0.1492" into "it moved 6.57 times its usual amount", which is
a sentence you can compare across industries of any size.

**Why the middle distance and not the average distance.** Because one bad
month must not be allowed to set the yardstick. This data has months where a
trading partner vanishes from the published figures and returns later. If the
yardstick were an average, those months would stretch it, and the detector
would go quiet exactly when the data got messy. The middle cannot be stretched
by one value — see Appendix B for the demonstration.

#### 2c. The 1.4826

```
0.0153 x 1.4826 = 0.0227
```

**This is a unit conversion and nothing else.** The same number every time, for
every industry, every month.

**What it converts.** The MAD and the standard deviation both describe spread,
but on different scales — the MAD comes out systematically smaller. For a
normal bell curve the relationship between them is fixed:

```
MAD  =  standard deviation x 0.67449
```

Turn that round to go the other way:

```
standard deviation  =  MAD / 0.67449  =  MAD x 1.4826
```

**Checked on random numbers** whose true spread is exactly 1.0:

| How many numbers | Raw MAD | × 1.4826 |
|---|---|---|
| 1,000 | 0.6415 | 0.9511 |
| 100,000 | 0.6746 | **1.0001** |
| 2,000,000 | 0.6745 | **1.0000** |

The raw MAD lands on 0.6745 every time, and multiplying by 1.4826 recovers the
true spread of 1.0.

**Why bother converting at all.** So that "3 of them" means what people expect
it to mean. The whole severity scale is built on the **three-sigma** convention
— three standard deviations. If we fed it raw MADs, every score would be
inflated by about 48%:

| | Ratio | Severity |
|---|---|---|
| With the 1.4826 | 0.1492 / 0.0227 = **6.57** | **79.4** |
| Without it | 0.1492 / 0.0153 = **9.75** | 85.8 |

**Same data, 6 points of severity apart**, purely because the yardstick was on
the wrong scale. The conversion keeps 63 meaning "about three standard
deviations" rather than "about three of some other unit".

**So: A's gap usually sits about 0.0227 from its normal.** That is its **usual
variation**.

### Step 3 — how far is this month, in A's own units

```
this month            +0.1151
A's normal            -0.0341
difference             0.1492

0.1492 / 0.0227  =  6.57
```

**October 2025 is 6.6 times A's usual variation away from A's normal.**

That sentence is the measurement. Everything after is formatting.

### Step 4 — allow for having only 21 months of history

```
6.57  ->  4.74
```

#### The problem this fixes

The 6.57 means "6.57 times A's usual variation". But that usual variation —
**0.0227** — was not handed to us. **We estimated it from 21 numbers.**

Had those 21 months fallen differently, we would have got a slightly different
figure, and the ratio would have come out differently too. **So 6.57 is built
on an uncertain yardstick, and it does not know it.**

With 21 numbers that uncertainty is real. With 500 it would be negligible.

#### How it is corrected — the t distribution

This is a standard, century-old statistical problem: *how surprising is a
value when the ruler used to measure it was itself estimated from a small
sample?* The answer is the **t distribution**, and the correction is a
**translation between two scales**.

Three steps, with A's numbers:

```
1. our yardstick came from 21 numbers, so use a
   t distribution with 20 degrees of freedom
   (degrees of freedom = how many numbers, minus one)

2. on that t curve, what fraction of months sit
   further out than 6.57?
       = 0.00000106
       = about 1 month in 945,000

3. on an ordinary bell curve, which value is
   exactly that rare?
       = 4.74
```

**So 6.57 on a 21-sample scale is exactly as rare as 4.74 on a bell curve.**
The number changes; the rarity does not. That is the whole operation — the
score is restated in a unit that does not depend on how much history there
happened to be.

A t curve has **fatter tails** than a bell curve: with few observations,
extreme-looking values are more common than they would be otherwise. So the
same value is *less* remarkable on a t curve, and the translation moves it
down.

#### What it costs, by how much history you have

Same ratio of 6.57 every time, only the number of months changing:

| Months of history | 6.57 becomes | Severity |
|---|---|---|
| 13 | 4.20 | 75.4 |
| **21** *(A's case)* | **4.74** | **79.4** |
| 30 | 5.10 | 81.7 |
| 60 | 5.67 | 84.9 |
| 120 | 6.06 | 86.7 |
| 1,000 | 6.50 | 88.5 |

**Short history is penalised; long history is barely touched.** At 1,000 months
6.57 is almost unchanged, because by then the yardstick is reliable.

**This is the only place in the whole calculation where anything is "pulled
back", and it is not a fudge factor** — it is a translation that keeps the
rarity fixed. In the real tool, any score resting on fewer than **24 months**
is also labelled **provisional** on screen, so the reader knows the discount
was applied.

### Step 5 — put it on 0–100

```
severity = 100 x (1 - e^(-4.74 / 3)) = 79.4
```

#### Why squash it at all

4.74 is a perfectly good answer, but it has no ceiling. One industry could
score 4.74 and another 40. **A number with no upper limit is awkward to sort,
filter with a slider, or put in a table**, so it is mapped onto 0–100.

#### What the curve does

| z | 0 | 1 | 2 | **3** | 4 | 6 | 9 | 20 |
|---|---|---|---|---|---|---|---|---|
| Severity | 0.0 | 28.3 | 48.7 | **63.2** | 73.6 | 86.5 | 95.0 | 99.9 |

Three deliberate properties:

| | |
|---|---|
| **z = 0 gives exactly 0** | perfectly normal scores zero |
| **it never reaches 100** | there is always headroom, so no two extremes tie at the top |
| **the gains shrink** | 3 → 4 adds **10 points**; 9 → 12 adds only **3** |

That third one matters. **The difference between "unusual" and "very unusual"
should matter more than the difference between "extreme" and "even more
extreme."** Once a month is clearly an outlier, how much of an outlier it is
stops being the useful question.

#### Why divide by 3, and not some other number

**Purely so the three-sigma convention lands on 63.** The divisor is the only
free choice here, and it is set by that convention:

| Divide by | z = 3 gives |
|---|---|
| 1 | 95.0 |
| 2 | 77.7 |
| **3** | **63.2** |
| 4 | 52.8 |

Dividing by 3 is what makes "z = 3" — the oldest convention in outlier work —
come out at **63**. That is the entire reason 63 is the default threshold on
the dashboard, and nothing was tuned to produce it.

#### It does not change any ranking

| z | 0.5 | 1 | 2 | 3 | 4.74 | 6 | 9 |
|---|---|---|---|---|---|---|---|
| Severity | 15.4 | 28.3 | 48.7 | 63.2 | **79.4** | 86.5 | 95.0 |

Always increasing. **Sorting by severity is identical to sorting by z**, so the
squashing is presentation only — it never promotes or demotes anything.

**A scores 79.4.**

Without the step-4 discount it would be **88.8**. The thin history costs it
9 points.

## What 79.4 actually means

**Almost nothing on its own, and it is important to say so.**

All the meaning is in the **4.74**. The 79.4 is that same number relabelled
onto a 0–100 scale. On the real data the rank correlation between severity and
the underlying z is **0.999998** — identical ordering. **No information is
added and none is lost.**

If someone asks what 79.4 means, the honest answer is:

> "It is 4.74 standard deviations, put on a 0–100 scale so it can be sorted
> and filtered. The 4.74 is the number that means something."

### What it is not

Three misreadings people reliably arrive at, all wrong:

| Misreading | Why it is wrong |
|---|---|
| "79% of something" | It is not a percentage of anything |
| "79.4% confident" | There is no probability statement anywhere in this calculation |
| "79% of the move" | It says nothing about pounds. A's £1,265m could have been £1.265bn and the severity would be identical |

### What it does mean, measured

This is the version worth quoting, because it comes from the data rather than
from the formula. Across the real scored industry-months:

| Severity at least | Share of industry-months | Roughly |
|---|---|---|
| 28 | 56.80% | 1 in 2 |
| 49 | 17.35% | 1 in 6 |
| 63 ← default | 6.43% | 1 in 16 |
| 74 | 2.45% | 1 in 41 |
| 79.4 ← A's score | 1.30% | 1 in 77 |
| 87 | 0.34% | 1 in 292 |

So: **"a severity of 79.4 is about as unusual as the top 1.3% of
industry-months in this dataset — roughly one month in 77."** That sentence
means something. "79.4" by itself does not.

### Where the scale tops out

| z | 9 | 12 | 15 | 20 | 25 | 98 |
|---|---|---|---|---|---|---|
| Severity | 95.02 | 98.17 | 99.33 | 99.87 | 99.9760 | 100.0000 |

By about **z = 25** it is 100 to four decimal places.

**A common slip:** putting z = 98 into the formula gives `1 − e^(−32.67)`
which is **1**, and it is easy to stop there and read the answer as 1. It is
then **multiplied by 100**, so the severity is **100** — the maximum, not the
minimum.

In the real data this never arises. **The largest z ever recorded is 7.03 and
the largest severity 90.4.** Nothing has ever come close to the ceiling, which
is a sign the scale is not being squashed against its top end.

### The fair answer if someone pushes

**"Why not just show the 4.74?"**

You could, and it would arguably be more informative. The 0–100 scale exists
so the threshold slider works and so non-specialists are not handed a z-score.

**The cost of that choice is exactly this confusion** — 79.4 looks like it
means something and it does not. That is why the three underlying z values are
kept in `alerts.csv` alongside, and why the dashboard calls severity *"a
browsing dial, not a test of significance"*.

---

## Why the same move scores differently — the point of all this

Give **B** the *identical* +0.1151 and run the identical five steps.

| | Its normal | Its usual variation | 0.1151 is how many? | **Severity** |
|---|---|---|---|---|
| **A** | −0.0341 | **0.0227** | 6.6 | **79.4** |
| **B** | 0.0000 | **0.2136** | 0.5 | **16.2** |

**Same number. 79 against 16.**

B's gap moves about 0.21 in an ordinary month, so 0.115 is nothing. A's moves
0.023, so 0.115 is unheard of.

**A 0.115 gap is extraordinary for A and unremarkable for B, and the score says
so.** That is the entire design.

---

## June 2025 — why we subtract the median at all

| | |
|---|---|
| A's own log change | **+0.3790** — its biggest in three years (+46.1%) |
| The five, sorted | A=0.3790, D=0.3976, **C=0.4396**, B=0.5878, E=0.8615 |
| Median | **+0.4396** |
| **A − median** | **−0.0606** |

Everything jumped, so the median jumped, so **A did nothing special** — it rose
*less* than the middle industry. Its gap is negative and entirely ordinary.

**Without subtracting the median this would look like the biggest shock in the
dataset.**

In the real tool this exact situation once produced 74 industries apparently
rising more than 25% in a single month. None of them had.

---

## Why the median and not the average

The obvious objection: **"the log already put every industry on the same scale,
so why not just average them?"**

That is the right question, and it has a precise answer.

### The log fixed the units. It did nothing about outliers.

The log makes a £30bn industry and a £300m industry comparable, because a ratio
has no units. **It does not make them comparable in influence.**

| | As a log |
|---|---|
| an industry that grows 2% | **+0.0198** |
| an industry that doubles | **+0.6931** |

Still **35 times apart**. Logs compress the scale; they do not flatten it. An
industry with a reporting glitch is still an outlier in log space, and an
average is still dragged by it.

### What the average does, holding everything else still

Take October 2025 and change **only E's step**, leaving A, B, C and D exactly
as they are:

| E's move | E as a log | **Median** | **Average** | A's gap using median | A's gap using average |
|---|---|---|---|---|---|
| +60% *(actual)* | +0.4700 | **+0.0953** | +0.1233 | **+0.1151** | +0.0871 |
| +200% | +1.0986 | **+0.0953** | +0.2490 | **+0.1151** | -0.0386 |
| +1,000% | +2.3979 | **+0.0953** | +0.5089 | **+0.1151** | -0.2985 |
| +10,000% | +4.6151 | **+0.0953** | +0.9523 | **+0.1151** | -0.7419 |
| +100,000% | +6.9088 | **+0.0953** | +1.4111 | **+0.1151** | -1.2007 |

**The median does not move at all.** The average climbs without limit, and A's
gap collapses with it — **even though nothing about A changed.**

### And it gets worse than imprecise. It flips the sign.

| | A's gap | Ratio | Severity | Direction |
|---|---|---|---|---|
| E rose 60%, **median** | +0.1151 | +6.57 | **79.4** | **up** |
| E rose 60%, average | +0.0871 | +5.34 | 75.0 | up |
| E rose 1,000%, **median** | +0.1151 | +6.57 | **79.4** | **up** |
| E rose 1,000%, average | **-0.2985** | **-11.65** | 87.9 | **down** |

**A rose 23%.** With the average, and a sufficiently extreme E, A would be
reported as having **fallen** unusually — severity 87.9, direction down.

**One industry's behaviour would have changed the sign of another industry's
finding.** That is not a loss of precision. It is a wrong answer.

### Why the median cannot do that

**The median asks what the middle industry did.** To move it you must move the
industry *in the middle* — and one industry cannot be both the middle and the
extreme at once. E can rise 100,000% and the median stays at +0.0953, because
E was never the middle one and still is not.

### The same argument applies twice over

This is not a one-off choice. **Middle values are used in both places:**

| Where | What it protects against |
|---|---|
| **Across industries** (Table 2) | one industry's glitch moving everyone's definition of normal |
| **Across months** (Steps 1 and 2) | one bad month in an industry's history setting its own yardstick |

Same reasoning each time. **This data has months where a trading partner
vanishes from the published figures and returns later.** If those could stretch
the yardstick, the detector would go quiet exactly when the data got messy.
## The part this example leaves out: there are three signals, not one

Everything above used **one** way of looking: the year-on-year comparison. The
real detector computes **three**, and takes whichever is strongest.

| Signal | The question it asks |
|---|---|
| **1 month** | is this month's level odd against its own recent run? |
| **Year on year** | ← **the one this whole document walks through** |
| **6-month drift** | has it been drifting for half a year, too gently for any single month to flag? |

All three are scored, then:

```python
severity = 100 * (1 - exp(-max(all three) / 3))     # strongest, not a blend
```

### Why it matters — the real June 2026 data

| Industry | 1 month | Year on year | 6-month drift | Winner | Severity |
|---|---|---|---|---|---|
| 85 Education | -0.10 | +5.19 | +5.39 | **6-month drift** | 83.4 |
| 66 Activities auxiliary to financ | +0.08 | -4.91 | -5.21 | **6-month drift** | 82.4 |
| 68 Real estate activities | -1.08 | -3.44 | -1.49 | **year on year** | 68.3 |
| 72 Scientific research and develo | +2.54 | +3.37 | +1.37 | **year on year** | 67.5 |
| 51 Air transport | -0.83 | -2.88 | -2.42 | **year on year** | 61.7 |

**The top two industries were caught by the drift signal, not the year-on-year
one.** Education's 1-month signal is −0.10, essentially nothing. A tool using
only one signal would have missed both.

**Why the strongest rather than an average:** averaging needs weights, and any
weights would be invented. Taking the strongest means *"if any of the three
ways of looking says this is odd, it is odd"*. All three are stored in
`alerts.csv`, so you can always see which one fired.

---

## Every month is scored, not just the latest

A fair question: the data runs to December 2025, so why look at October?

**Because every month is scored.** October is simply where the move was put in
this example. Here is **every scoreable month of A**:

| Month | A − median | A's normal | Variation | Ratio | **Severity** |
|---|---|---|---|---|---|
| Jan 2024 | -0.0437 | — | — | — | *not scored, only 0 months* |
| Feb 2024 | -0.0241 | — | — | — | *not scored, only 1 months* |
| Mar 2024 | -0.0341 | — | — | — | *not scored, only 2 months* |
| Apr 2024 | -0.0468 | — | — | — | *not scored, only 3 months* |
| May 2024 | +0.0000 | — | — | — | *not scored, only 4 months* |
| Jun 2024 | -0.0139 | — | — | — | *not scored, only 5 months* |
| Jul 2024 | -0.0424 | — | — | — | *not scored, only 6 months* |
| Aug 2024 | -0.0144 | — | — | — | *not scored, only 7 months* |
| Sep 2024 | -0.0239 | — | — | — | *not scored, only 8 months* |
| Oct 2024 | -0.0191 | — | — | — | *not scored, only 9 months* |
| Nov 2024 | -0.0046 | — | — | — | *not scored, only 10 months* |
| Dec 2024 | -0.0244 | — | — | — | *not scored, only 11 months* |
| Jan 2025 | -0.0494 | -0.0240 | 0.0150 | -1.69 | 40.5 |
| Feb 2025 | -0.0408 | -0.0241 | 0.0151 | -1.11 | 29.8 |
| Mar 2025 | -0.0130 | -0.0243 | 0.0199 | +0.57 | 16.9 |
| Apr 2025 | -0.0064 | -0.0241 | 0.0165 | +1.07 | 29.1 |
| May 2025 | -0.0580 | -0.0240 | 0.0206 | -1.65 | 40.5 |
| Jun 2025 | -0.0606 | -0.0241 | 0.0248 | -1.47 | 37.3 |
| Jul 2025 | -0.0416 | -0.0243 | 0.0255 | -0.68 | 19.9 |
| Aug 2025 | -0.0761 | -0.0244 | 0.0255 | -2.03 | 46.9 |
| Sep 2025 | -0.0676 | -0.0292 | 0.0224 | -1.71 | 41.9 |
| Oct 2025 | +0.1151 | -0.0341 | 0.0227 | +6.57 | **79.4** |
| Nov 2025 | -0.0228 | -0.0292 | 0.0234 | +0.27 | 8.5 |
| Dec 2025 | -0.0310 | -0.0244 | 0.0267 | -0.25 | 7.9 |

**October is the only month that clears 63. December scores 7.9** — it was
scored, it just is not unusual.

This is a better thing to show than one month alone, because **a detector that
only ever fires is not detecting anything.**

### Notice the normal and the variation move

Look at the two middle columns. A's normal drifts −0.0240, −0.0241, −0.0292,
−0.0341, and the variation changes too. **They are rebuilt from scratch for
every month**, using only that month's own history. There is no single fixed
yardstick.

### Why keep the history scored

| | |
|---|---|
| **You cannot judge one month alone** | "five industries fired" means nothing until you know the normal rate |
| **Revisions change the past** | a delivery once restated a month that had already been scored |
| **Questions arrive late** | "what happened last spring?" needs spring scored |
| **It is how the thresholds were justified** | the claim that 63 fires on ~6% of industry-months comes from all the rows, not one month |

---

## The scope of the real thing

```
77 industries  x  57 months  x  3 measures  x  2 comparison bases
                                    = 26,334 possible
                                      25,086 actually scored
```

Plus rolled-up section and GDP-grouping rows: **32,538 rows in total.**

Three measures — **inflow, outflow and PFI** — each scored separately, because
an industry can move on what it receives without moving on what it pays.

### Eleven SIC codes are never scored, for two different reasons

**Nine are below the size floor** — under £50m average monthly inflow:

| | Mean inflow |
|---|---|
| SIC 05 Coal, 07 Metal ores, 12 Tobacco | **£0m** |
| SIC 97, 98, 99 household and extraterritorial | £2–4m |
| SIC 03 Fishing, 15 Leather, 37 Sewerage, 91 Libraries | £19–47m |

At that size a single payment moves the series 20%, so a score would be noise
with a number attached. **Better to say nothing than to say something
unreliable.**

**One is large but unscoreable.** **SIC 19** averages **£552m**, well over the
floor, but a structural break reset its baseline and it has not yet rebuilt
enough history. That is industry **E** in this example.

### And 33 of 90 months are never scored

The first twelve have no year-earlier figure, then roughly twelve more are
needed before "normal" exists. **Every series starts dark for about two
years** — and an industry that breaks goes dark again for a year afterwards.

---

## One thing that surprises people

**Severity is identical for MoM and YoY.** The score is computed once per
industry-month from the three signals, none of which is a month-on-month
comparison.

Switching the comparison on the dashboard changes the **£ change**, the
**% change** and the **common component** shown beside the score. **It does not
change the score.**

Volunteer this rather than be caught by it.

---

## The program does not decide anything

Worth being clear, because "how does it pick?" is a natural question.

**Two separate stages:**

**Scoring** is mechanical. Every industry, every month, every measure, both
bases. 25,086 rows. No thresholds, no choices, no judgement — three numbers in,
one ratio out, repeated.

**Selecting** happens in the *dashboard*, not the detector. Sort by severity,
then cut at the slider. **That is the only place anything is "picked", and you
control it.** Drag it to 40 and more appears; to 90 and almost nothing does.
Nothing is recomputed — you are moving a line through a list that already
exists.

---

## If you only remember five things

1. **Severity is a distance measured in that industry's own units** — not
   pounds, not percent. A 13-point gap is extraordinary for A and
   unremarkable for B.
2. **Subtract what everyone did**, or a month when the whole economy moves
   looks like 88 separate shocks.
3. **Middle values, not averages**, everywhere — so one bad month cannot set
   the yardstick.
4. **The 0–100 number carries no meaning of its own.** It is the z relabelled
   so a slider can filter it. 63 is just the formula at z = 3.
5. **Nothing is selected by the program.** Everything is scored; you choose
   where to cut.

---


---
---

# Part 2 — Confidence

Severity says **how far from normal**. It cannot say **whether anything
happened**. That is what confidence is for, and it is the column people skip.

## Why it is needed — one number, three stories

A's PFI went **1025 → 1265**, a rise of **240**. Severity **79.4**.

Here are three completely different ways that exact same 240 could arise. The
severity is **79.4 in all three**, because severity only sees the total.

### Scenario 1 — broad-based

```
P:  200 -> 248   +48
Q:  195 -> 243   +48
R:  210 -> 258   +48
S:  205 -> 253   +48
T:  215 -> 263   +48
```

Every partner paid more. **Real, widespread growth.**

### Scenario 2 — one partner did it

```
P:  200 -> 420  +220      <- 92% of the whole move
Q:  195 -> 200    +5
R:  210 -> 215    +5
S:  205 -> 210    +5
T:  215 -> 220    +5
```

**Probably a single contract.** Real money changing hands, but not an industry
trend.

### Scenario 3 — a partner vanished

```
P:  200 -> 225   +25
Q:  195 -> 215   +20
R:  210 -> 235   +25
S:  205 -> 225   +20
T:  215 ->   0  -215      <- VANISHED from the published data
U:    0 -> 365  +365      <- APPEARED
```

**Nobody need have changed what they paid at all.** T's figure was withheld
this month, U's was withheld last month. The 240 is largely an accident of
what was published.

### The three verdicts

| | Presence | Biggest partner | Breadth | **Confidence** | **The "Why" column** |
|---|---|---|---|---|---|
| 1 | 0% | 20% | 100% | **medium** | *provisional — only 21 months of baseline* |
| 2 | 0% | **92%** | 100% | **medium** | *92% of the move is a single counterparty* |
| 3 | **62%** | 152% | 83% | **low** | *driven by counterparties appearing or disappearing* |

**Without confidence, scenario 3 would sit in Movers looking exactly like
scenario 1** — and someone would report a reporting artefact as growth.

## The nine tests

They run **in a fixed order and the first match wins**. Nothing is weighted or
averaged. **The "Why" column is the wording of the test that fired** — no text
is written by hand.

| # | Test | Fires when | Label |
|---|---|---|---|
| 1 | Whole economy moved | median industry change ≥ **±20%** | low |
| 2 | On a known structural break | in the break register | low |
| 3 | Partners appearing or vanishing | presence ≥ **50%** | low |
| 4 | Unidentified-payer share jumped | ≥ **±20 points** | low |
| 5 | Most cells withheld | > **50%** | low |
| 6 | One partner carries the move | top ≥ **70%** | medium |
| 7 | Concentrated in a few partners | breadth < **40%** | medium |
| 8 | Partly presence-driven | presence ≥ **25%** | medium |
| 9 | Thin baseline | < **24 months** | medium |
| — | nothing fired | — | **high** |

Trace scenario 3: test 1 no (the median was 10%), test 2 no, **test 3 fires at
62%** → stop. Label `low`, and the Why column is that test's wording.

Scenario 2: tests 1–5 no, **test 6 fires at 92%** → stop. Medium.

## How tests 1 and 2 are calculated

### Test 1 — "the whole economy moved"

**You already know this number.** It is the **median across industries** from
Table 2 — converted from logs back into a percentage.

```
Table 2, Oct 2025:  median log change = +0.0953
                    as a percentage   = +10.0%     -> does not fire
Table 2, Jun 2025:  median log change = +0.4396
                    as a percentage   = +55%       -> FIRES
```

The test asks: *was the middle industry's own change this month enormous?* If
it was, no single industry's move can be read as its own news.

### Test 2 — "on a known structural break"

A **structural break** is a month where the level shifts and **stays**
shifted — a step, not a spike. **Industry E in our example is exactly this:**
1000 until Dec 2024, then 1600 onwards.

**How they are found.** For every candidate month, split the series in two and
ask *"how much better do two separate levels fit than one?"* That is a
least-squares score, and it has a single sharp peak at a genuine step. The size
of the shift is then measured with medians, so a couple of odd months cannot
inflate it. COVID months are excluded as candidates — that was a shock, not a
reclassification.

Fourteen were found in the real data. The largest:

| Industry | Break month | Level change | Cause |
|---|---|---|---|
| 79 Travel agency, tour operat | Mar 2022 | **+371%** | level shift |
| 19  | Oct 2025 | **-66%** | suppression-driven |
| 85 Education | Mar 2025 | **-54%** | reclassification |
| 08 Other mining and quarrying | Aug 2021 | **+67%** | level shift |
| 23 Manufacture of other non-m | Aug 2021 | **+55%** | level shift |
| 90 Creative, arts and enterta | Mar 2022 | **+68%** | level shift |

They are written to `outputs/breaks.csv`, and the test is a lookup: *is this
industry-month in that list?*

**Why a break means low confidence:** either side of it the series sits at a
different level, so a year-on-year comparison spanning it compares two
different things. The move is real arithmetic and meaningless economics.

## How the other seven are calculated

| # | Test | Calculation |
|---|---|---|
| 3 | Presence | `\|newly + absent\| ÷ \|total change\|` from the counterparty split |
| 4 | SIC 00 shift | share of inflow from unidentified payers, compared across two 5-month windows |
| 5 | Suppressed | withheld cells ÷ 89 possible partners |
| 6 | Top partner | `\|biggest contribution\| ÷ \|total\|` |
| 7 | Breadth | fraction of partners moving the **same direction** as the total |
| 8 | Presence again | same metric as test 3, weaker threshold |
| 9 | Baseline | count of usable prior months |

## Important: the tests are not all run on every row

**Four are cheap. Five need a full counterparty decomposition**, which is only
done for the **top 10 per month, measure and basis.**

| Test input | Computed on |
|---|---|
| `common_pct` (test 1) | **25,086** of 25,086 (100.0%) |
| `break_flag` (test 2) | **25,086** of 25,086 (100.0%) |
| `suppressed_share` (test 5) | **25,086** of 25,086 (100.0%) |
| `baseline_months` (test 9) | **25,086** of 25,086 (100.0%) |
| `presence_share` (tests 3, 8) | **3,420** of 25,086 (13.6%) |
| `top_counterparty_share` (test 6) | **3,420** of 25,086 (13.6%) |
| `breadth` (test 7) | **3,420** of 25,086 (13.6%) |
| `sic00_share_shift` (test 4) | **3,420** of 25,086 (13.6%) |

You can see the cut in the real June 2026 data:

| Rank | Industry | Severity | Presence | Top partner | Breadth | Confidence |
|---|---|---|---|---|---|---|
| 1 | 85 Education | 83.4 | 0% | 69% | 54% | medium |
| 2 | 66 Activities auxiliary t | 82.4 | 2% | 102% | 49% | medium |
| 3 | 68 Real estate activities | 68.3 | 1% | 53% | 55% | high |
| 4 | 72 Scientific research an | 67.5 | 2% | 89% | 49% | medium |
| 5 | 51 Air transport | 61.7 | 107% | 79% | 50% | low |
| 6 | 09 Mining support service | 60.8 | 3% | 65% | 57% | high |
| 7 | 06 Extraction of crude pe | 59.7 | 17% | 34% | 66% | low |
| 8 | 47 Retail trade, except o | 58.5 | 0% | 15% | 65% | high |
| 9 | 56 Food and beverage serv | 56.8 | 4% | 45% | 62% | high |
| 10 | 95 Repair of computers an | 51.0 | 60% | 57% | 74% | low |
| 11 | 35 Electricity, gas, stea | 46.6 | **—** | **—** | **—** | high |
| 12 | 30 Manufacture of other t | 45.1 | **—** | **—** | **—** | high |
| 13 | 22 Manufacture of rubber  | 42.9 | **—** | **—** | **—** | high |

**Below rank 10 those columns are empty**, so tests 3, 4, 6, 7 and 8 are
skipped and the checklist falls through to the cheap ones.

**The consequence, and it is worth volunteering:** an industry ranked 11th with
a vanished counterparty will show **high** — not because it passed the artefact
tests, but because they were never run. The blank columns are the only signal.
**If you are investigating something outside the top 10, open "Why did it
move?" and read the presence share yourself.**

## Three things to say about the labels

**"High" is impossible for A.** With 21 months, test 9 always fires. Same
scenario 1, different history length:

| History | Confidence | Why |
|---|---|---|
| 21 months | medium | *provisional* |
| **24 months** | **high** | *broad-based* |

**"Low" does not mean wrong.** It means *we could not rule out a known
artefact*. Scenario 3 might be genuine growth — these numbers cannot tell.

**"High" does not mean right.** It means none of nine tests found anything. The
absence of a red flag, not a positive verdict.


---
---

# Part 3 — The structural detector

A **second, completely separate** detector. It never looks at the money total.
It asks whether the **shape** of an industry's trading changed.

An industry can receive exactly the same amount two years running while the
set of businesses paying it changes completely. The money says nothing
happened. Something did.

## Step 1 — nine facts about the trading, every month

Worked on **SIC 85 Education, June 2026 — structural score 100.0**:

| Feature | This month | Its own median | Its own spread | **z** |
|---|---|---|---|---|
| how many partners pay it | 80 | 82 | 1.4826 | -1.35 |
| concentration by value | 0.4032 | 0.6350 | 0.0440 | **-5.27** |
| concentration by volume | 0.0860 | 0.1344 | 0.0430 | -1.13 |
| its largest single partner | 0.6229 | 0.7946 | 0.0278 | **-6.18** |
| paid to itself | 0.0861 | 0.0389 | 0.0090 | **+5.28** |
| from unidentified payers | 0.6811 | 0.2389 | 0.0276 | **+16.02** |
| partners gained or lost | 0.0244 | 0.0000 | 0.0157 | +1.55 |
| average payment size | 7,463 | 7,723 | 1138.2597 | -0.23 |
| network position | 0.0102 | 0.0149 | 0.0022 | -2.10 |

## Step 2 — standardise within the industry

**The same arithmetic as severity, done nine times:**

```
z = (this month - its own median) / its own spread
```

Take *from unidentified payers*. Education normally gets **24%** of its money
from payers with no industry code. In June 2026 it was **68%**:

```
(0.6811 - 0.2389) / 0.0276 = +16.02
```

**Sixteen times its own normal variation.** That is the Education
reclassification, found by a route completely independent of severity.

Standardising **within** each industry is essential. Without it the model would
simply discover that industries differ from each other — true, and useless.

> **A bug worth knowing about.** The spread uses MAD, as severity does. But
> **churn is zero in most months**, so its median and its MAD are both zero,
> which nulled 95% of rows and left the model 360 of 7,783 to learn from.
> There is now a fallback to the standard deviation when MAD collapses.

## Step 3 — the Isolation Forest

The only genuinely new idea here, and it is simpler than the name.

**Imagine separating one month from all the others by asking random yes/no
questions** about those nine numbers. *Is self-share above 0.05? Is
unclassified-share below 0.3?*

- an **ordinary** month sits in the crowd and takes **many** questions to pin down
- an **odd** month is out on its own and is isolated in **two or three**

The algorithm builds **300 random question-trees** and measures how few
questions each month needed on average. **Fewer questions = stranger month.**

It looks for points that are **easy to separate**, not points far from an
average. That is why it is good at **combinations**: a month where churn is
mildly up, concentration mildly down and unclassified sharply up gets isolated
quickly, even though no single feature would trip a rule.

**Why not nine separate rules?** Because the combination is the signal. Any one
feature moving is ordinary.

## Step 4 — onto 0–100

```
raw = -decision_function(...)            flip, so higher = stranger
rescale between the 1st and 99th percentile of all raw scores
clip to 0-100
```

**This is why the structural score is not comparable to severity.** It is a
**rank within this dataset**, rescaled. Education's 100.0 means *"the most
unusual shape in the data"*, not *"infinitely unusual"*. Severity's 63 has an
arithmetic meaning; structural's 100 does not.

**The flag is separate.** `contamination = 0.03` tells the model to mark the
strangest **3%**. That is the one real judgement in the method, and it sets how
long the list is — not what counts as odd.

## The sentence for the room

> "Nine facts about who an industry trades with, each measured against that
> industry's own normal, then an algorithm that asks how few random questions
> it takes to single that month out. Education's June 2026 shape needed very
> few — its unclassified share was sixteen times its normal variation."


---
---

# Part 4 — How the two combine, and what reaches the screen

## Two detectors, two files

| | File | Score column | Reads |
|---|---|---|---|
| **Level** | `alerts.csv` | `severity` | **one** number a month — the money |
| **Structural** | `structural.csv` | `structural_score` | **nine** numbers a month — the shape |

## The "Kind of anomaly" control does three different things

**Level — the money moved.** The severity list. Structural is ignored.

**Structural — the shape changed.** The page **discards the level table** and
builds a different one from `structural.csv`, with its own score, a plain
*"What changed"* sentence, and an **"Also a level alert?"** column.

**Both together.** The level list, filtered to keep only rows whose
`(industry, month)` also appears in the structural flagged set. **A set
intersection — that is the entire mechanism:**

```python
keys  = set(zip(flagged.sic2, flagged.month))
fired = fired[[(c, m) in keys for c, m in zip(fired.code, fired.month)]]
```

## They overlap far less than people expect

| | |
|---|---|
| Level alerts (severity ≥ 63) | **256** |
| Structural alerts | **231** |
| **Both** | **10** |
| Structural only | 221 — **96%** of structural |
| Level only | 246 |

**96% of structural alerts are invisible to the level detector.** They are
almost entirely finding different things — which is the justification for
having both. If they overlapped heavily the second one would be redundant.

## What "Both together" actually gets you

**Ten industry-months in five years:**

| Month | Industry | Severity | Structural | What changed |
|---|---|---|---|---|
| Jun 2026 | 85 Education | 83.4 | **100.0** | more arriving from unclassified payers (+16.0 vs normal); smaller shar |
| May 2026 | 85 Education | 83.8 | **100.0** | more arriving from unclassified payers (+17.1 vs normal); smaller shar |
| Apr 2026 | 85 Education | 83.9 | **100.0** | more arriving from unclassified payers (+16.0 vs normal); smaller shar |
| Mar 2026 | 85 Education | 84.4 | **100.0** | more arriving from unclassified payers (+14.5 vs normal); smaller shar |
| Sep 2024 | 94 Activities of member | 79.6 | **70.4** | more arriving from unclassified payers (+3.8 vs normal); smaller share |
| Aug 2024 | 94 Activities of member | 76.0 | **80.1** | more activity within the industry (+4.4 vs normal); more arriving from |

**Education appears four months running** — its money moved unusually *and* its
trading reorganised at the same time. That is the reclassification: payers
stopped being identified, so the total and the shape moved together.

**These are the strongest signals the tool produces**, because two independent
methods agree.

**But remember the scales differ.** Education at severity 83.4 and structural
100.0 does not mean the structural finding is stronger. Different scales, same
range, no relationship between them.

---

## What actually reaches the screen

A natural worry: there are 25,086 scored rows, so how is anything readable?

**They never compete for the screen.** Pick a month and a measure and you are
down to 77 before any filtering:

| | Rows |
|---|---|
| All scored rows (every month/measure/basis/level) | 32,538 |
| Division level only | 25,086 |
| One month (Jun 2026) | 462 |
| One measure (PFI) | 154 |
| One basis (YoY) | **77** ← the real pool |

Everything else in the 25,086 belongs to a **different month, measure or
basis**, and you reach it by changing a control.

### Then each page applies its own rule

| Page | Rule | Shows in Jun 2026 |
|---|---|---|
| **Overview** | top **3** by severity, from those clearing 63 | 3 |
| **Movers** | sorted by severity, **then** by size — slider default | **12 of 77** |
| **Outliers** | everything clearing the severity slider **and** the confidence filter | **4** |

**Movers ranks. Outliers filters.** In Movers all 77 stay in the table and the
slider only controls how many rows you see, so you can always drag to 77.
Outliers excludes anything below the threshold:

| Severity slider | Industries shown |
|---|---|
| 0 | 72 |
| 30 | 25 |
| 49 | 7 |
| 63 *(default)* | 4 |
| 74 | 2 |
| 87 | 0 |

### So "how does it decide what to show?"

**It does not. You do.**

Nothing is hidden by the detector. Every one of the 77 has a score, all are in
`alerts.csv`, and **the only thing between you and any of them is a slider
position you control.**

The defaults — **63** and **top 12** — exist so the first screen is readable
rather than 77 rows deep. Starting points, not judgements.

**One honest caveat.** The Overview's "top 3" is the one place something is
genuinely cut, and it is fixed at 3 with no control. If four industries moved
unusually, the fourth is not on that page. **The Overview is a headline;
Movers and Outliers are where you look properly.**


---
---

# Appendix A — the discount for short history

This moved into **Step 4**, where it is used. The short version: the yardstick
was estimated from 21 numbers, so the score is translated onto a scale that
does not depend on how much history there was. See Step 4 for the arithmetic
and the table of what it costs at different history lengths.

---

# Appendix B — why the middle distance, not the average distance

Step 2 uses the **middle** of the 21 distances. The obvious alternative is the
average of them, which is what a standard deviation is built on. Here is why
we do not.

## Why not just use the standard deviation

One bad month destroys it. 24 months of history, then one bad month added:

| | Our measure | Standard deviation |
|---|---|---|
| Clean history | 0.66 | 1.21 |
| One bad month | 0.81 | 9.88 |
| **Change** | **1.2x** | **8.2x** |

And what that does to scoring a genuine move:

| History | Our measure | Standard deviation |
|---|---|---|
| Clean | **4.88** | 2.52 |
| One bad month | **4.00** | **0.10** |

**One bad month makes the standard deviation blind** — the real move scores
0.10 instead of 2.52. Ours goes 4.88 to 4.00: dented, not erased.

This dataset has months where a trading partner vanishes and comes back. With a
standard deviation the detector would go quiet exactly when the data got messy.

**Be honest if asked:** ours is resistant, not immune. It still moved 20%. It
just does not collapse.

---

# Appendix C — a caveat about this example

**D and E were deliberately given the same growth rate** so the median would
sit still and A would never be the middle industry. With only five industries
the median is whichever one lands in the middle — and if that is A, its gap
becomes zero and the example teaches nothing.

With the real **88 industries** this is automatic.

**If someone asks why the tool is not run on a handful of key sectors, this is
the answer:** five industries cannot give you a stable "what everyone did".
