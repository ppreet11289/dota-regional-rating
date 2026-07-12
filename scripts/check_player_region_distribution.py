"""
Check region distribution across a known Indian player's recent matches.
"""

import json
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

REGION_NAMES = {
    1: "US WEST", 2: "US EAST", 3: "EUROPE", 5: "SINGAPORE", 6: "DUBAI",
    7: "AUSTRALIA", 8: "STOCKHOLM", 9: "AUSTRIA", 10: "BRAZIL",
    11: "SOUTHAFRICA", 12: "PW TELECOM SHANGHAI", 13: "PW UNICOM",
    14: "CHILE", 15: "PERU", 16: "INDIA", 17: "PW TELECOM GUANGDONG",
    18: "PW TELECOM ZHEJIANG", 19: "JAPAN", 20: "PW TELECOM WUHAN",
    25: "PW UNICOM TIANJIN", 37: "TAIWAN", 38: "ARGENTINA",
}


def fetch_json(url, retries=3, delay=2.0):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}"
        except Exception as e:
            last_err = e
        time.sleep(delay * (attempt + 1))
    raise RuntimeError(f"Failed after {retries} attempts: {last_err}")


def get_player_match_ids(account_id, limit=20):
    url = f"https://api.opendota.com/api/players/{account_id}/matches?limit={limit}"
    matches = fetch_json(url)
    return [m["match_id"] for m in matches]


def get_match_region(match_id):
    url = f"https://api.opendota.com/api/matches/{match_id}"
    match = fetch_json(url)
    return match.get("region")


if __name__ == "__main__":
    ACCOUNT_ID = 362433020

    print(f"Fetching recent match IDs for account {ACCOUNT_ID}...")
    match_ids = get_player_match_ids(ACCOUNT_ID, limit=20)
    print(f"Got {len(match_ids)} match IDs. Checking region for each...")

    region_counts = Counter()
    details = []
    for i, mid in enumerate(match_ids):
        try:
            region = get_match_region(mid)
            region_name = REGION_NAMES.get(region, f"UNKNOWN ({region})")
            region_counts[region_name] += 1
            details.append({"match_id": mid, "region": region, "region_name": region_name})
            print(f"  [{i+1}/{len(match_ids)}] match {mid}: region {region} ({region_name})")
        except Exception as e:
            print(f"  [{i+1}/{len(match_ids)}] match {mid}: FAILED ({e})")
        time.sleep(1)

    print("\n--- Region distribution across this player's matches ---")
    for region_name, count in region_counts.most_common():
        pct = 100 * count / len(details) if details else 0
        print(f"  {region_name}: {count} ({pct:.0f}%)")

    out_path = DATA_DIR / f"player_{ACCOUNT_ID}_region_distribution.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"account_id": ACCOUNT_ID, "matches": details,
                    "region_counts": dict(region_counts)}, f, indent=2)
    print(f"\nSaved details to {out_path}")