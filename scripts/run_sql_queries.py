import sqlite3
import pandas as pd
from pathlib import Path

# Paths
DATA_PATH = Path("data/raw/dpwh_flood_control_projects.csv")

def run_week8_queries():
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    # Initialize SQLite database in memory
    conn = sqlite3.connect(":memory:")

    # Register dataset as a table
    df.to_sql("dpwh_flood_control_projects", conn, index=False, if_exists="replace")

    print("✅ Successfully loaded working dataset into SQLite!\n")
    return conn

if __name__ == "__main__":
    conn = run_week8_queries()