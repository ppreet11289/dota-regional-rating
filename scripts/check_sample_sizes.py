"""
Week 1 go/no-go check.

Before writing a single line of rating-model code, answer this: is there
enough data, per player, in the India cluster to say anything statistically
meaningful? If not, the project needs to widen scope (South Asia broadly,
or SEA) before Stage 2 starts — better to find that out now than in week 6.

This script assumes you've already run pull_matches.py and have:
  - data/cluster_counts_last_90d.json  (cluster -> total match count)
  - data/matches_<cluster_id>.json     (raw matches for a chosen cluster)

It does NOT pull data itself — it only analyzes what's already pulled.
Keeping these separate means you can re-run this cheaply while iterating
on which cluster/time-window to use, without re-hitting the API each time.
"""

import json
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_matches(cluster_id: int) -> list:
    path = DATA_DIR / f"matches_{cluster_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run pull_matches.py with this cluster_id "
            f"first — this script only analyzes data that already exists, "
            f"it doesn't fetch anything."
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("rows", [])


def summarize_cluster(cluster_id: int) -> dict:
    matches = load_matches(cluster_id)
    n_matches = len(matches)

    # NOTE: public_matches gives you MATCH-level rows, not player-level.
    # It does not directly tell you how many matches a given individual
    # player has — that requires joining against player-level match
    # history (a separate pull, per-player, via /players/{account_id}/matches
    # or the public_player_matches table). This script only tells you the
    # aggregate match volume for the cluster, which is a necessary first
    # check, but NOT the same as "matches per player" — don't conflate
    # the two when writing this up. The per-player pull is the next step
    # if aggregate volume looks viable.

    rank_tiers = Counter(m.get("avg_rank_tier") for m in matches if m.get("avg_rank_tier"))
    durations = [m["duration"] for m in matches if m.get("duration")]

    return {
        "cluster_id": cluster_id,
        "total_matches_in_window": n_matches,
        "matches_with_rank_tier_data": sum(rank_tiers.values()),
        "distinct_rank_tiers_seen": len(rank_tiers),
        "rank_tier_distribution": dict(rank_tiers.most_common()),
        "avg_duration_seconds": (
            sum(durations) / len(durations) if durations else None
        ),
    }


def viability_check(summary: dict, min_matches_threshold: int = 2000) -> str:
    """
    Rough, honest gut-check — not a rigorous statistical test, just a first
    filter. 2000 is a placeholder threshold, not derived from anything;
    the real bar is whatever gives enough matches PER PLAYER once you do
    the per-player pull. Adjust once you have that number, and record the
    reasoning in research_log.md rather than silently changing it.
    """
    n = summary["total_matches_in_window"]
    if n < min_matches_threshold:
        return (
            f"LOW VOLUME ({n} matches). Aggregate match count this low makes "
            f"it unlikely you'll get enough matches per individual player. "
            f"Consider widening to South Asia broadly or SEA before "
            f"proceeding to Stage 2."
        )
    return (
        f"Aggregate volume looks plausible ({n} matches) — but this is NOT "
        f"sufficient on its own. Next step: pull per-player match history "
        f"for a sample of players in this cluster and check the actual "
        f"matches-per-player distribution before concluding this is viable."
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python check_sample_sizes.py <cluster_id> [<cluster_id> ...]")
        print(
            "Get cluster IDs from data/cluster_counts_last_90d.json "
            "(produced by pull_matches.py) — don't guess them."
        )
        sys.exit(1)

    for cid in sys.argv[1:]:
        cid = int(cid)
        summary = summarize_cluster(cid)
        print(json.dumps(summary, indent=2))
        print(viability_check(summary))
        print("-" * 60)
