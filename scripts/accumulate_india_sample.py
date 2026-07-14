"""
Automates what you were doing manually: repeatedly pull batches of SEA
match accounts, check country_code, and keep going until we hit the
target of 30 India-tagged accounts with >=50 matches — or a safety cap
on iterations. Uses the same checkpoint file, picks up where you left off.
Safe to interrupt with Ctrl+C — progress saves after every account.
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
TARGET_VIABLE_ACCOUNTS = 30
MAX_ITERATIONS = 40


def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"checked": {}}


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


def count_viable_india_accounts(state):
    match_counts = state.get("match_counts", {})
    viable = 0
    for aid, code in state["checked"].items():
        if code and code.upper() == "IN":
            mc = match_counts.get(aid)
            if mc is not None and mc >= MIN_MATCHES_THRESHOLD:
                viable += 1
    return viable


if __name__ == "__main__":
    state = load_checkpoint()
    state.setdefault("match_counts", {})

    for iteration in range(MAX_ITERATIONS):
        viable_so_far = count_viable_india_accounts(state)
        print(f"\n=== Iteration {iteration+1}/{MAX_ITERATIONS} | "
              f"viable India accounts so far: {viable_so_far}/{TARGET_VIABLE_ACCOUNTS} ===")

        if viable_so_far >= TARGET_VIABLE_ACCOUNTS:
            print("Target reached.")
            break

        already_checked = set(int(k) for k in state["checked"].keys())
        match_ids = get_recent_sea_match_ids(N_MATCHES_PER_BATCH, offset_hours=iteration * 6)

        all_account_ids = set()
        for mid in match_ids:
            try:
                all_account_ids.update(get_account_ids_for_match(mid))
            except Exception as e:
                print(f"  match {mid} failed: {e}")
            time.sleep(REQUEST_DELAY)

        new_account_ids = all_account_ids - already_checked
        print(f"  {len(new_account_ids)} new accounts to check this iteration")

        for aid in new_account_ids:
            try:
                code = get_country_code(aid)
                state["checked"][str(aid)] = code
                if code and code.upper() == "IN":
                    mc = get_total_match_count(aid)
                    state["match_counts"][str(aid)] = mc
                    flag = "VIABLE" if mc >= MIN_MATCHES_THRESHOLD else "too few matches"
                    print(f"    India-tagged: account {aid}, {mc} matches ({flag})")
            except Exception as e:
                print(f"    account {aid} failed: {e}")
            time.sleep(REQUEST_DELAY)
            save_checkpoint(state)

    final_viable = count_viable_india_accounts(state)
    total_checked = len(state["checked"])
    total_india = sum(1 for c in state["checked"].values() if c and c.upper() == "IN")

    print(f"\n=== Final summary ===")
    print(f"Total accounts checked: {total_checked}")
    print(f"India-tagged: {total_india}")
    print(f"India-tagged AND >=50 matches (viable): {final_viable}/{TARGET_VIABLE_ACCOUNTS}")

    save_json(
        {"total_checked": total_checked, "total_india_tagged": total_india,
         "viable_accounts": final_viable, "target": TARGET_VIABLE_ACCOUNTS},
        "accumulation_summary.json",
    )
    print("Saved to data/accumulation_summary.json")