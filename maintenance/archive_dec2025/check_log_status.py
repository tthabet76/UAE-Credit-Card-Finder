import sqlite3
import pandas as pd
import os

DB_FILE = os.path.join(os.getcwd(), 'credit_card_data.db')
conn = sqlite3.connect(DB_FILE)
query = "SELECT status, COUNT(*) as count FROM llm_interaction_log GROUP BY status"
df = pd.read_sql_query(query, conn)
print(df)
conn.close()
