# Regional Rating Uncertainty in Dota 2

**Status:** Week 1 — data infrastructure + sample-size validation. No results yet.

## Motivation

Skill-rating systems used in matchmaking and scouting (TrueSkill, Glicko-2)
are Bayesian: a rating is a belief (mean + uncertainty) that narrows as more
games are observed. That convergence assumption is validated on data-rich
scenes (EU, China, Korea pro/high-MMR pools). It's untested whether it holds
in thinner regional pools, where individual players may have far fewer
recorded matches and higher variance from inconsistent teammates. If it
doesn't hold, any scouting or ranking system built on standard rating
methods will systematically under- or mis-rate players from underrepresented
regions — which matters directly for talent identification in regions
without established competitive infrastructure.

See `CLAIM.md` for the exact, falsifiable version of this, written before
any data was pulled.

## Repo structure

```
dota-regional-rating/
├── CLAIM.md              # pre-registered hypothesis, do not edit after data pull
├── README.md             # this file — doubles as the eventual writeup
├── research_log.md       # dated working notes, private reasoning trail
├── scripts/
│   ├── pull_matches.py           # OpenDota Explorer queries -> raw match data
│   └── check_sample_sizes.py     # week 1: is there enough data per region?
├── data/                 # raw + processed data (gitignored if large)
└── notebooks/            # exploratory analysis, kept messy on purpose
```

## Data source

[OpenDota](https://www.opendota.com/) — public API + SQL Explorer over their
`public_matches` / `public_player_matches` tables. Free tier: 50,000 calls/month,
60 req/min. No API key needed for Explorer SQL queries.

Important schema note (found in week 1, not assumed): `public_matches` does
**not** have a `region` column. It has `cluster` (server cluster ID), which
maps to region via a separate lookup table. Don't filter on a `region` field
that doesn't exist — resolve cluster → region first. See
`scripts/pull_matches.py` for the current mapping and a TODO to verify it's
current, since cluster IDs can change.

## Week 1 checklist

- [ ] Run `check_sample_sizes.py` — how many matches/players actually exist
      for the India cluster vs. comparison regions, in a reasonable time
      window? This determines if the project is viable as scoped.
- [ ] If India-only is too thin, decide: widen to South Asia broadly, or to
      SEA. Record the decision and why in `research_log.md` — don't just
      silently change scope.
- [ ] Read Glicko-2 paper, then TrueSkill paper (links in research_log.md).
- [ ] Commit early and often, even broken scripts — the commit history is
      part of the evidence that this was built over months, not a weekend.

## Non-goals (deliberately out of scope)

- No user-facing app or dashboard. Output is code + a written result.
- No attempt at a fully general "correction framework" — one behavioral
  signal, tested rigorously, is the target. See CLAIM.md.
- Not claiming to have invented a new rating system — this extends/tests
  existing ones (TrueSkill, Glicko-2) against a specific, real gap.

## Findings

(Nothing yet — to be filled in as Stage 1/2/3 complete, with plots and
honest reporting of negative results if that's what happens.)
