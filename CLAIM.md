# Pre-registered claim

Written and committed before any analysis was run, so results can be checked
against it rather than the claim being adjusted to fit whatever was found.

## Primary hypothesis

Standard Bayesian skill-rating systems (TrueSkill, Glicko-2) converge to a
stable, low-uncertainty rating faster in server regions with large player
pools and deep matchmaking history than in thinner regional pools.

**Falsifiable version:**

> For players on the India cluster with between 50 and 100 ranked matches
> in the sample window, the mean TrueSkill posterior standard deviation
> (sigma) will be higher than the mean sigma for EU West or SE Asia players
> at the same match-count bucket, controlling for rank tier.

This is checkable against a specific number once the data is pulled. If
India-cluster sigma is *not* meaningfully higher (say, within ~10% of the
comparison region at the same match count), the primary hypothesis is
**false** and the project pivots to reporting why the assumption didn't
hold — not to re-defining "thin" until it's true.

## Secondary hypothesis (the actual contribution)

A behavioral feature extracted from match telemetry — starting candidate:
item-timing efficiency relative to role/hero benchmark — added as a
low-weight auxiliary signal to the rating update will reduce time-to-stable-rating
(fewer matches needed to reach a target sigma) compared to outcome-only
TrueSkill, for the thin-data region specifically.

**Falsifiable version:**

> Adding the behavioral signal reduces the number of matches needed to reach
> sigma < [threshold, set after seeing baseline convergence curves in Stage 1
> — record the exact number here once set, before running the corrected model]
> by at least 15% for India-cluster players, without degrading predictive
> accuracy (win-probability calibration) on held-out matches.

If this doesn't hold, the honest result is: "outcome-only rating converges
just as fast/faster than the corrected version, here's the likely reason
(e.g., the behavioral signal is noisier than outcome data, or the benchmark
normalization was too coarse)." That is still a legitimate finding for the
writeup.

## What would make me abandon this project direction entirely

- If region/cluster sample sizes for India are too small even in the widest
  reasonable window (e.g., <500 total matches after filtering) to say
  anything statistically meaningful — see `scripts/check_sample_sizes.py`,
  run this in week 1 before investing further.
- If TrueSkill sigma turns out NOT to differ by region at all (see primary
  hypothesis above) — in that case there's no problem to correct for, and
  continuing would mean solving a problem that doesn't exist.

## Log

- [DATE TO FILL IN] — claim written, no data pulled yet.





## What would make me abandon this project direction entirely

- If region/cluster sample sizes for India are too small even in the widest
  reasonable window (e.g., <500 total matches after filtering) to say
  anything statistically meaningful — see `scripts/check_sample_sizes.py`,
  run this in week 1 before investing further.
- If TrueSkill sigma turns out NOT to differ by region at all (see primary
  hypothesis above) — in that case there's no problem to correct for, and
  continuing would mean solving a problem that doesn't exist.

## Log

- 2026-07-13 — claim written, no data pulled yet.
- 2026-07-13 — PIVOT. See "Revision 1" below.

---

## Revision 1 — India's dedicated cluster is not a viable data source

**What was found, empirically, not assumed:**

- OpenDota's `public_matches.cluster` field maps to a region via
  `constants/cluster` → `constants/region`. Cluster 261 is the only
  cluster tagged to region 16 ("India").
- Checked cluster 261 across 8 independent 6-hour windows spanning 48
  hours (with a 24h buffer for OpenDota's ingestion lag): **zero matches**
  in every single window.
- Same windows, SEA cluster 152 (region 5, Singapore): 122,729 matches
  total. Not a close comparison — India's cluster is not "thin," it is
  inactive.
- Cross-checked against a single confirmed Indian player (Steam
  `country_code: "in"`, verified via player object): 20/20 of their most
  recent ranked matches were played on cluster 152 (SEA), zero on 261.

**What this means for the original hypothesis:**

The original framing assumed a real (if sparse) India-region player
population, separable by cluster, whose rating convergence could be
compared against a data-rich region. That population, as a *cluster*, does
not meaningfully exist. Indian players are not thinly spread across their
own server — they are almost entirely absorbed into the SEA population,
indistinguishable from other SEA players by cluster or region alone.

This does not kill the project. It changes what "regional" has to mean.

**Revised primary hypothesis:**

> Players who self-identify as Indian (via Steam profile `country_code =
> "in"`) but who play predominantly within the SEA server population
> (cluster 151/152/153/etc.) are not meaningfully distinguishable from
> other SEA players by any signal *currently used* in standard skill
> rating — meaning if there is a scouting/rating disadvantage for this
> subgroup, it isn't from data sparsity in the TrueSkill-convergence sense
> originally proposed. It's from lacking any feature that separates them
> from a much larger, more diverse pool at all.

**Revised falsifiable version:**

> For a sample of N players with `country_code = "in"` who have >=50
> matches primarily on SEA clusters, standard TrueSkill/Glicko ratings
> computed on their SEA match history converge (reach a target sigma) at
> a similar rate to a random sample of non-India SEA players with the same
> match count — i.e., outcome-only rating convergence is NOT where the
> problem is, since they're pooled with a large population, not isolated.
> [N and the target sigma to be set once a sample of India-tagged players
> is identified — record the exact numbers here before running the
> comparison, same pre-registration discipline as before.]

**What the actual contribution becomes:**

Not "fix rating convergence for a thin population" (that problem doesn't
exist here) but: can a behavioral/telemetry signal (e.g. item-timing
efficiency, positional data) identify talent *within* the India-tagged
subgroup that outcome-based rating, pooled with the broader SEA
population, does not surface — because win/loss-based rating has no
mechanism to flag "this player is unusually strong for their subgroup,"
only "this player wins often against whoever they're matched with,"
which in a large diverse pool may wash out subgroup-specific standout
performance.

**New known limitation to state upfront, not hide:** `country_code` is a
self-reported Steam profile field. Not all players fill it in, and it may
be inaccurate for some. Any sample built on it needs to acknowledge this
as a real constraint on how representative the "Indian player" sample is,
not something to gloss over in the writeup.

**What would make me abandon *this* revised direction:**

- If very few players in accessible match samples actually have
  `country_code = "in"` set (i.e., the field is too sparsely filled to
  build a usable sample at all) — check this before building anything
  further on top of it.
- If, once a sample is built, there's no meaningful behavioral signal
  difference between India-tagged and other SEA players at all — a
  legitimate negative result, reportable honestly, but a sign the
  "hidden talent" framing doesn't hold up.