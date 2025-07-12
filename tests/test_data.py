import psycopg2
import pandas as pd

# Expand display settings
pd.set_option("display.max_rows", 20)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

# DB connection
conn = psycopg2.connect(
    dbname="propdb",
    user="propuser",
    password="proppass123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Function to fetch and display table
def fetch_table_data(table_name):
    cur.execute(f"SELECT * FROM {table_name}")
    colnames = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    return pd.DataFrame(rows, columns=colnames)

# FULL LIST OF TABLES
tables = [
    "users",
    "cases",
    "invoices",
    "ledger",
    "registration_requests",
    "company_settings",
    "commission_records",
    "ed_closures",
    "ed_summary"
]

# Loop and display
for table in tables:
    try:
        df = fetch_table_data(table)
        print(f"\n📊 {table.upper()} TABLE DATA")
        if df.empty:
            print("No data found.")
        else:
            print(df.head(20))
    except Exception as e:
        print(f"❌ Error fetching {table}: {e}")

# Close connections
cur.close()
conn.close()
