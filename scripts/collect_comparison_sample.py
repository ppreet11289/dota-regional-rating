"""
Collect 30 non-India SEA accounts with >=50 matches, to compare against
the 30 India-tagged accounts already found. Reuses accounts already
checked, only fetches match counts for ones we haven't run /wl on yet.
"""

import json
import time
from pathlib import Path

from pull_matches import pull_matches_for_cluster, save_json
from check_player_region_distribution import fetch_json

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHECKPOINT_FILE = DATA_DIR / "checked_accounts.json"

SEA_CLUSTER = 152
N_MATCHES_PER_BATCH = 15
REQUEST_DELAY = 3.0
MIN_MATCHES_THRESHOLD = 50
TARGET_COMPARISON_ACCOUNTS = 30
MAX_ITERATIONS = 20


def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"checked": {}, "match_counts": {}}


def save_checkpoint(state):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_recent_sea_match_ids(n_matches, offset_hours=0):
    now = int(time.time())
    end_time = now - 24 * 60 * 60 - offset_hours * 60 * 60
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


def get_total_match_count(account_id):
    result = fetch_json(f"https://api.opendota.com/api/players/{account_id}/wl")
    return (result.get("win", 0) or 0) + (result.get("lose", 0) or 0)


def get_current_comparison_accounts(state):
    match_counts = state.get("match_counts", {})
    comparison = []
    for aid, code in state["checked"].items():
        is_india = code and code.upper() == "IN"
        if not is_india:
            mc = match_counts.get(aid)
            if mc is not None and mc >= MIN_MATCHES_THRESHOLD:
                comparison.append(aid)
    return comparison


if __name__ == "__main__":
    state = load_checkpoint()
    state.setdefault("match_counts", {})

    print("Checking match counts for existing non-India accounts first...")
    candidates_needing_wl = [
        aid for aid, code in state["checked"].items()
        if not (code and code.upper() == "IN") and aid not in state["match_counts"]
    ]
    print(f"  {len(candidates_needing_wl)} existing accounts to check")

    for aid in candidates_needing_wl:
        current = len(get_current_comparison_accounts(state))
        if current >= TARGET_COMPARISON_ACCOUNTS:
            break
        try:
            mc = get_total_match_count(int(aid))
            state["match_counts"][aid] = mc
        except Exception as e:
            print(f"    account {aid} failed: {e}")
        time.sleep(REQUEST_DELAY)
        save_checkpoint(state)

    current = len(get_current_comparison_accounts(state))
    print(f"After checking existing accounts: {current}/{TARGET_COMPARISON_ACCOUNTS}")

    for iteration in range(MAX_ITERATIONS):
        current = len(get_current_comparison_accounts(state))
        if current >= TARGET_COMPARISON_ACCOUNTS:
            print("Target reached.")
            break

        print(f"\n=== Fresh batch iteration {iteration+1}/{MAX_ITERATIONS} | "
              f"{current}/{TARGET_COMPARISON_ACCOUNTS} ===")
        already_checked = set(int(k) for k in state["checked"].keys())
        match_ids = get_recent_sea_match_ids(N_MATCHES_PER_BATCH, offset_hours=iteration * 6 + 500)

        all_account_ids = set()
        for mid in match_ids:
            try:
                all_account_ids.update(get_account_ids_for_match(mid))
            except Exception as e:
                print(f"  match {mid} failed: {e}")
            time.sleep(REQUEST_DELAY)

        new_account_ids = all_account_ids - already_checked
        print(f"  {len(new_account_ids)} new accounts to check")

        for aid in new_account_ids:
            if len(get_current_comparison_accounts(state)) >= TARGET_COMPARISON_ACCOUNTS:
                break
            try:
                code = get_country_code(aid)
                state["checked"][str(aid)] = code
                if not (code and code.upper() == "IN"):
                    mc = get_total_match_count(aid)
                    state["match_counts"][str(aid)] = mc
            except Exception as e:
                print(f"    account {aid} failed: {e}")
            time.sleep(REQUEST_DELAY)
            save_checkpoint(state)

    final_comparison = get_current_comparison_accounts(state)
    print(f"\n=== Final summary ===")
    print(f"Comparison accounts (non-India, >=50 matches): "
          f"{len(final_comparison)}/{TARGET_COMPARISON_ACCOUNTS}")
    print(f"Account IDs: {final_comparison[:TARGET_COMPARISON_ACCOUNTS]}")

    save_json(
        {"comparison_accounts": final_comparison[:TARGET_COMPARISON_ACCOUNTS],
         "target": TARGET_COMPARISON_ACCOUNTS},
        "comparison_sample.json",
    )
    print("Saved to data/comparison_sample.json")