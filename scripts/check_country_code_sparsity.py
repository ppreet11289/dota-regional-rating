"""
Check whether country_code (loccountrycode) is populated often enough
among SEA-cluster players to build a usable "India-tagged player" sample.
Persists results across runs — run this multiple times to accumulate a
big enough sample to actually find India-tagged players.
"""

import json
import time
from collections import Counter
from pathlib import Path

from pull_matches import pull_matches_for_cluster, save_json
from check_player_region_distribution import fetch_json

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHECKPOINT_FILE = DATA_DIR / "checked_accounts.json"

SEA_CLUSTER = 152
N_MATCHES_PER_RUN = 15
REQUEST_DELAY = 3.0


def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"checked": {}}


def save_checkpoint(state):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_recent_sea_match_ids(n_matches):
    now = int(time.time())
    end_time = now - 24 * 60 * 60
    window_start = end_time - 6 * 60 * 60
    result = pull_matches_for_cluster(SEA_CLUSTER, window_start, end_time, limit=n_matches)
    rows = result.get("rows", [])
    return [r["match_id"] for r in rows]


def get_account_ids_for_match(match_id):
    match = fetch_json(f"https://api.opendota.com/api/matches/{match_id}")
    players = match.get("players", [])
    return [p["account_id"] for p in players if p.get("account_id")]


def get_country_code(account_id):
    result = fetch_json(f"https://api.opendota.com/api/players/{account_id}")
    profile = result.get("profile", {})
    return profile.get("loccountrycode")


if __name__ == "__main__":
    state = load_checkpoint()
    already_checked = set(int(k) for k in state["checked"].keys())
    print(f"Loaded checkpoint: {len(already_checked)} accounts already checked.")

    print(f"Pulling {N_MATCHES_PER_RUN} recent SEA cluster ({SEA_CLUSTER}) match IDs...")
    match_ids = get_recent_sea_match_ids(N_MATCHES_PER_RUN)
    print(f"Got {len(match_ids)} match IDs.")

    all_account_ids = set()
    for i, mid in enumerate(match_ids):
        print(f"  [{i+1}/{len(match_ids)}] fetching players for match {mid}...")
        try:
            account_ids = get_account_ids_for_match(mid)
            all_account_ids.update(account_ids)
        except Exception as e:
            print(f"    FAILED: {e}")
        time.sleep(REQUEST_DELAY)

    new_account_ids = all_account_ids - already_checked
    print(f"\nFound {len(all_account_ids)} accounts this run, {len(new_account_ids)} are new.")
    print("Checking country_code for new accounts only...")

    for i, aid in enumerate(new_account_ids):
        try:
            code = get_country_code(aid)
            state["checked"][str(aid)] = code
            print(f"  [{i+1}/{len(new_account_ids)}] account {aid}: country_code = {code}")
        except Exception as e:
            print(f"  [{i+1}/{len(new_account_ids)}] account {aid}: FAILED ({e})")
        time.sleep(REQUEST_DELAY)
        save_checkpoint(state)

    country_counts = Counter(
        (code.upper() if code else code) for code in state["checked"].values()
    )
    total = len(state["checked"])
    populated = sum(v for k, v in country_counts.items() if k)
    india_tagged = country_counts.get("IN", 0)

    print("\n--- Cumulative results across all runs so far ---")
    print(f"Total accounts checked (all-time): {total}")
    if total:
        print(f"Have ANY country_code set: {populated} ({100*populated/total:.0f}%)")
    print(f"Tagged 'in' (India) specifically: {india_tagged}")
    print(f"\nCheckpoint saved to {CHECKPOINT_FILE} — run this script again to keep accumulating.")

    summary = {
        "total_checked_all_time": total,
        "populated_all_time": populated,
        "india_tagged_all_time": india_tagged,
        "country_distribution": dict(country_counts),
    }
    save_json(summary, "country_code_sparsity_summary.json")