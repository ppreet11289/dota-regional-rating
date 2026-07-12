"""
Quick diagnostic: what is the most recent match timestamp actually present
in OpenDota's public_matches table right now?
"""

import time
from pull_matches import run_explorer_query

if __name__ == "__main__":
    result = run_explorer_query("SELECT MAX(start_time) AS most_recent FROM public_matches;")
    rows = result.get("rows", [])
    if not rows or rows[0].get("most_recent") is None:
        print("No rows returned at all — table may be empty or query malformed.")
        print(result)
    else:
        most_recent = int(rows[0]["most_recent"])
        now = int(time.time())
        lag_hours = (now - most_recent) / 3600
        print(f"Most recent match timestamp in table: {most_recent}")
        print(f"Current time: {now}")
        print(f"Data lag: {lag_hours:.1f} hours behind real-time")