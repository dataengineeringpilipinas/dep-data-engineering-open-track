#!/usr/bin/env python3
"""Run the Week 8 SQL business questions (sql/business_questions.sql) on the cleaned data.

Run from the repository root (after scripts/transform.py):
    python scripts/run_sql_queries.py

It loads data/processed/dpwh_flood_control_projects_cleaned.csv into an in-memory
SQLite table called projects_cleaned, runs each query in the .sql file and prints
the results. Nothing is written to disk.
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

DATA_FILE = Path("data/processed/dpwh_flood_control_projects_cleaned.csv")
SQL_FILE = Path("sql/business_questions.sql")
TABLE = "projects_cleaned"


def split_queries(sql_text: str) -> list[tuple[str, str]]:
    """Return (title, query) pairs. The title is the comment line after 'QUESTION n'."""
    pairs = []
    for chunk in sql_text.split(";"):
        lines = chunk.strip().splitlines()
        code = "\n".join(l for l in lines if not l.strip().startswith("--")).strip()
        if not code:
            continue
        comments = [l.strip("- ").strip() for l in lines if l.strip().startswith("--")]
        idx = next((i for i, c in enumerate(comments) if c.startswith("QUESTION")), None)
        title = " ".join(c for c in comments[idx:] if c) if idx is not None else "Query"
        pairs.append((title, code))
    return pairs


def main() -> None:
    if not DATA_FILE.exists():
        sys.exit(f"{DATA_FILE} not found. Run scripts/transform.py first.")
    conn = sqlite3.connect(":memory:")
    pd.read_csv(DATA_FILE).to_sql(TABLE, conn, index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 45)
    for title, query in split_queries(SQL_FILE.read_text(encoding="utf-8")):
        print(f"\n{title}\n" + "-" * min(len(title), 100))
        print(pd.read_sql_query(query, conn).to_string(index=False))
    conn.close()


if __name__ == "__main__":
    main()
