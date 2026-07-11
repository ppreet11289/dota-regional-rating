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
