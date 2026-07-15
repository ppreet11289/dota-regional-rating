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
  
  ## 2026-07-12 — Session 2

- What I did: verified a real Indian player (account_id 362433020, country_code
  "in", found via OpenDota's /proPlayers endpoint) and checked which
  cluster/region their matches actually run on, instead of trusting an
  unverified cluster-to-region list found online.
- What happened: their most recent match had region:5, which OpenDota's
  own /constants/region endpoint confirms is SINGAPORE — not region:16
  (INDIA). One data point isn't enough to conclude anything on its own,
  so next step is checking a larger sample of this player's matches
  (script: check_player_region_distribution.py) to see the actual split
  between India and SEA/Singapore servers.
- What surprised me: expected a confirmed Indian player's matches to
  mostly show region:16 (India). Finding region:5 instead raises the
  possibility that Indian players get routed to or choose the SEA server
  more often than their own regional one.
- Why this matters for the project: if that pattern holds across more
  players, it's not just a data-labeling issue — it may be direct evidence
  FOR the original hypothesis in CLAIM.md. A thin India-specific
  matchmaking pool that can't sustain itself would show up exactly this
  way: players nominally "Indian" but playing predominantly on a larger
  neighboring region's servers because the India-specific pool is too
  small/slow to find matches in.
- Open question: what's the actual India vs SEA split across more players
  (not just one)? Running check_player_region_distribution.py next to
  find out before drawing any conclusion.

  ## 2026-07-13 — Session 1

- What I did: fixed a case-sensitivity bug (India tagged "IN" uppercase,
  code checked lowercase "in", was undercounting as zero). Ran the
  accumulating country_code checker across multiple batches.
- What happened: 299 accounts checked total, 161 (54%) have loccountrycode
  set at all, 15 (~5% of total, ~9% of populated) tagged "IN" specifically.
- What this means: country_code-based identification is viable — India-
  tagged players are a real, findable, if small, slice of the SEA pool.
- Open question: 15 accounts is a start, not enough for the revised
  hypothesis (needs players with >=50 matches each, per CLAIM.md
  Revision 1). Need to keep accumulating, then separately check how many
  matches each of these 15 (and future finds) actually has.



  ## 2026-07-14 — Session 1

- What I did: fixed a case-sensitivity bug found by manually inspecting
  raw output (India tagged "IN" uppercase, code checked lowercase "in",
  was silently undercounting as zero). Ran the accumulating country_code
  checker to 299 total accounts checked. Then checked total match counts
  for all India-tagged accounts found so far via OpenDota's /wl endpoint.
- What happened: 15 India-tagged accounts found (~5% of 299 checked, 54%
  of which had loccountrycode populated at all). Of those 15, 11 have
  >=50 recorded matches (several with 3,000-6,800+), meeting the sample
  threshold set in CLAIM.md Revision 1. 4 accounts showed exactly 0
  matches via /wl — likely private match-history settings (separate from
  having a public profile/country code), not accounts with genuinely no
  games.
- What this means: the revised hypothesis is buildable. 11 viable
  accounts is a real starting sample, though likely still too small for
  a robust statistical comparison — worth continuing to accumulate more
  before finalizing sample size.
- Caveat to remember for the writeup: /wl reports OpenDota-tracked
  matches, not necessarily true lifetime match count — treat as "matches
  available to analyze," not literal career total. Also: match-history
  privacy settings mean some India-tagged players are excluded from any
  match-count-based analysis entirely, which is itself a form of sample
  bias worth naming explicitly (not hiding).
- Open question: how many India-tagged accounts, cumulatively, is
  "enough" for a real comparison sample? Need to decide and pre-register
  a target N in CLAIM.md rather than deciding after seeing how the
  numbers look.

  ## 2026-07-14 — Session 2

- What I did: ran accumulate_india_sample.py to target completion.
- What happened: checked 1,638 total SEA-cluster accounts. 51 tagged
  "IN" (~3.1% true India rate in this pool — a real, useful number for
  the writeup, not just "small"). 30 of those 51 meet the >=50 match
  threshold set in CLAIM.md.
- What this means: sample size target (30) reached. Data collection
  phase for the India-tagged subgroup is essentially done for now.
- Open question / next step: still need a matched comparison sample —
  30 random non-India SEA players (same match-count range) to actually
  test the revised hypothesis against. Then move to Stage 2: implement
  TrueSkill/Glicko and compare rating behavior between the two groups.