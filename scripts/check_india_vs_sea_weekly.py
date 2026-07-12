"""
Targeted follow-up: is cluster 261 (India) really at zero, or was the
6-hour window just unlucky? Check a full week instead.
"""

import time
from pull_matches import run_explorer_query, save_json


def count_matches_for_cluster(cluster_id, min_start_time, max_start_time):
    sql = f"""
        SELECT COUNT(*) AS match_count
        FROM public_matches
        WHERE cluster = {cluster_id}
          AND start_time > {min_start_time}
          AND start_time < {max_start_time};
    """
    result = run_explorer_query(sql)
    rows = result.get("rows", [])
    return int(rows[0]["match_count"]) if rows else 0


if __name__ == "__main__":
    now = int(time.time())
    end_time = now - 24 * 60 * 60

    india_cluster = 261
    sea_cluster = 152

    TOTAL_HOURS = 48
    CHUNK_HOURS = 6
    n_chunks = TOTAL_HOURS // CHUNK_HOURS

    india_total = 0
    sea_total = 0
    chunk_results = []

    for i in range(n_chunks):
        chunk_end = end_time - i * CHUNK_HOURS * 60 * 60
        chunk_start = chunk_end - CHUNK_HOURS * 60 * 60

        print(f"Chunk {i+1}/{n_chunks} (window ending {chunk_end})...")
        india_chunk = count_matches_for_cluster(india_cluster, chunk_start, chunk_end)
        print(f"  India cluster: {india_chunk}")
        time.sleep(2)

        sea_chunk = count_matches_for_cluster(sea_cluster, chunk_start, chunk_end)
        print(f"  SEA cluster:   {sea_chunk}")
        time.sleep(2)

        india_total += india_chunk
        sea_total += sea_chunk
        chunk_results.append({
            "chunk_start": chunk_start, "chunk_end": chunk_end,
            "india_count": india_chunk, "sea_count": sea_chunk,
        })

    result = {
        "total_hours_covered": TOTAL_HOURS,
        "india_cluster_261_total": india_total,
        "sea_cluster_152_total": sea_total,
        "chunk_breakdown": chunk_results,
    }
    save_json(result, "india_vs_sea_comparison.json")
    print(f"\n--- {TOTAL_HOURS}-hour totals ---")
    print(f"India (cluster 261): {india_total}")
    print(f"SEA (cluster 152):   {sea_total}")
    print("\nSaved to data/india_vs_sea_comparison.json")