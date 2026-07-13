"""
Discover the ACTUAL current columns of public_matches, since avg_mmr
apparently no longer exists — check Postgres's own schema info directly
instead of trusting any assumption.
"""

from pull_matches import run_explorer_query

if __name__ == "__main__":
    sql = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'public_matches'
        ORDER BY ordinal_position;
    """
    result = run_explorer_query(sql)
    rows = result.get("rows", [])
    print("Actual current columns in public_matches:")
    for r in rows:
        print(f"  {r['column_name']}: {r['data_type']}")