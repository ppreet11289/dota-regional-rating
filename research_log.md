# Research log

Private working notes. Write 3-4 sentences after every session: what you
tried, what happened, what you'd do differently. This is what lets you
defend decisions months later — most of the reasoning behind a choice is
gone from memory within weeks if it isn't written down here.

---

## Reading list (Week 1)

- Glicko-2 paper (Mark Glickman) — read first, shorter, and the author
  explains the sparse-data rating-uncertainty problem directly, which is
  the actual problem this project is about.
- TrueSkill paper (Herbrich, Minka, Graepel, Microsoft Research) — read
  second, more math-dense, but the standard system OpenDota-adjacent tools
  compare against.
- OpenDota API docs (docs.opendota.com) and the `odota/core` GitHub repo's
  `sql/create_tables.sql` — ground truth for what fields actually exist,
  rather than assuming based on tutorials.

## [DATE] — Session 1

- What I did:
- What happened:
- What I'd change next time:
- Open question carried to next session:

---

## Template for future entries

## [DATE] — Session N

- What I did:
- What happened / what I found:
- What surprised me or contradicted my assumption:
- What I'd change next time:
- Open question carried to next session:





## 2026-07-12 — Session 1

- What I did: got pull_matches.py running against OpenDota's live Explorer API.
- What happened: hit three real bugs in order — Cloudflare 403 (fixed with
  User-Agent header), then a query timeout (public_matches is huge, had to
  shrink the window and drop COUNT(DISTINCT)), then zero rows returned
  because the table has ~20hr ingestion lag (found via check_data_freshness.py,
  fixed by offsetting the window). Finally got real cluster-level match
  counts back — 44 distinct clusters in a 6-hour window.
- What surprised me: the ingestion lag. Assumed the table was closer to
  real-time.
- Open question: which cluster ID is actually India — couldn't find a
  reliable mapping online, so next step is empirically checking via a
  known Indian pro player's match history instead of trusting a
  cluster->region list.