"""
Pull public match data from OpenDota's Explorer endpoint.

OpenDota exposes a free SQL-over-HTTP interface at:
    https://api.opendota.com/api/explorer?sql=<url-encoded query>

This queries their `public_matches` table directly. No API key required
for this tier (50,000 calls/month, 60 req/min — plenty for this project;
each Explorer call can return many rows, so you don't need one call per match).

IMPORTANT — verify before relying on this:
`public_matches` schema (per odota/core's sql/create_tables.sql) is:
    match_id, match_seq_num, radiant_win, start_time, duration,
    avg_mmr, num_mmr, lobby_type, game_mode, avg_rank_tier,
    num_rank_tier, cluster

There is NO `region` column. Region is inferred from `cluster`, which is
a server cluster ID. The cluster -> region mapping below is a starting
point pulled from community sources (Steam/Dota forums), NOT verified
directly against Valve's or OpenDota's own source. Cluster IDs do change
over time and this list may be incomplete or stale — confirm against
current data before trusting any region-level conclusion built on it.
A quick sanity check: query cluster counts and cross-reference against
players you know play on a given server, or against OpenDota's own
per-region MMR distribution endpoint (/distributions) if it still exists
in the current API.

Run this file, don't just read it — the honest first step is to actually
hit the API and see what comes back, not to assume this mapping is correct.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OPENDOTA_EXPLORER_URL = "https://api.opendota.com/api/explorer"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Starting point only — VERIFY. Community-sourced cluster->region mapping,
# not pulled from an authoritative Valve/OpenDota source. Treat as a
# hypothesis to check against real query results, not a fact.
CLUSTER_TO_REGION_GUESS = {
    # cluster_id: "region label"
    # Fill in after running `SELECT cluster, COUNT(*) FROM public_matches
    # GROUP BY cluster ORDER BY 2 DESC;` and cross-referencing counts/
    # known player behavior. Do not trust a copied list without checking.
}


def run_explorer_query(sql: str, retries: int = 3, delay: float = 3.0) -> dict:
    url = f"{OPENDOTA_EXPLORER_URL}?sql={urllib.parse.quote(sql)}"
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            last_err = f"HTTP {e.code}: {body}"
            time.sleep(delay * (attempt + 1))
        except Exception as e:  # noqa: BLE001 - want to retry on anything transient
            last_err = e
            time.sleep(delay * (attempt + 1))
    raise RuntimeError(f"Explorer query failed after {retries} attempts: {last_err}")


def get_cluster_counts(min_start_time: int, max_start_time: int) -> dict:
    """
    Step 1, always run this first: how many matches per cluster exist in
    your chosen time window? This is the actual sample-size check, and it
    should happen before any modeling work, not after.
    """
    sql = f"""
        SELECT cluster, COUNT(*) AS match_count
        FROM public_matches
        WHERE start_time > {min_start_time} AND start_time < {max_start_time}
        GROUP BY cluster
        ORDER BY match_count DESC;
    """
    return run_explorer_query(sql)


def pull_matches_for_cluster(cluster_id, min_start_time, max_start_time, limit=50000):
    sql = f"""
        SELECT match_id, match_seq_num, radiant_win, start_time, duration,
               lobby_type, game_mode, avg_rank_tier, num_rank_tier, cluster
        FROM public_matches
        WHERE cluster = {cluster_id}
          AND start_time > {min_start_time}
          AND start_time < {max_start_time}
        ORDER BY start_time DESC
        LIMIT {limit};
    """
    return run_explorer_query(sql)


def save_json(obj: dict, filename: str) -> Path:
    out_path = DATA_DIR / filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return out_path


if __name__ == "__main__":

    now = int(time.time())
    end_time = now - 24 * 60 * 60          # 24h buffer past the ~20h lag
    window_start = end_time - 6 * 60 * 60  # 6-hour window before that

    print("Pulling cluster counts for a 6-hour window, offset for ingestion lag...")
    counts = get_cluster_counts(window_start, end_time)
    path = save_json(counts, "cluster_counts_last_6h.json")
    print(f"Saved to {path}")
    print(
        "Next: open this file, look at which cluster IDs have the highest "
        "match_count, and cross-reference against known Indian server "
        "cluster IDs before assuming which one is India."
    )

