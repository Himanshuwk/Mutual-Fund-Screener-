import pandas as pd
import sqlite3
import os

os.makedirs("db", exist_ok=True)

csv_path = "data/nav_history_5y.csv"
db_path = "db/nav_data.db"

chunk_size = 500_000

conn = sqlite3.connect(db_path)

for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size)):
    chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")

    chunk.to_sql(
        "nav_data",
        conn,
        if_exists="append" if i > 0 else "replace",
        index=False
    )

    print(f"Inserted chunk {i+1}")

conn.close()

print("✅ Database created")
