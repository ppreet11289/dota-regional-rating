"""
For each India-tagged account found so far, check total recorded match
count via OpenDota's /wl endpoint (win + loss = total tracked matches).
"""

import json
import time
from pathlib import Path

from pull_matches import save_json
from check_player_region_distribution import fetch_json

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHECKPOINT_FILE = DATA_DIR / "checked_accounts.json"

REQUEST_DELAY = 3.0
MIN_MATCHES_THRESHOLD = 50


def load_india_tagged_accounts():
    with open(CHECKPOINT_FILE, encoding="utf-8") as f:
        state = json.load(f)
    return [
        int(aid) for aid, code in state["checked"].items()
        if code and code.upper() == "IN"
    ]


def get_total_match_count(account_id):
    result = fetch_json(f"https://api.opendota.com/api/players/{account_id}/wl")
    win = result.get("win", 0) or 0
    lose = result.get("lose", 0) or 0
    return win + lose


if __name__ == "__main__":
    india_accounts = load_india_tagged_accounts()
    print(f"Found {len(india_accounts)} India-tagged accounts to check: {india_accounts}")

    results = []
    for i, aid in enumerate(india_accounts):
        try:
            total = get_total_match_count(aid)
            meets_threshold = total >= MIN_MATCHES_THRESHOLD
            results.append({"account_id": aid, "total_matches": total,
                             "meets_threshold": meets_threshold})
            flag = "OK" if meets_threshold else "too few"
            print(f"  [{i+1}/{len(india_accounts)}] account {aid}: {total} matches ({flag})")
        except Exception as e:
            print(f"  [{i+1}/{len(india_accounts)}] account {aid}: FAILED ({e})")
        time.sleep(REQUEST_DELAY)

    viable = [r for r in results if r["meets_threshold"]]
    print(f"\n--- Results ---")
    print(f"Checked: {len(results)} accounts")
    print(f"Meet >={MIN_MATCHES_THRESHOLD} match threshold: {len(viable)}")

    save_json(
        {"threshold": MIN_MATCHES_THRESHOLD, "results": results, "n_viable": len(viable)},
        "india_accounts_match_counts.json",
    )
    print("Saved to data/india_accounts_match_counts.json")