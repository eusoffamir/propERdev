import psycopg2

conn = psycopg2.connect(
    dbname='propdb',
    user='propuser',
    password='proppass123',
    host='localhost',
    port='5432'
)
cur = conn.cursor()
cur.execute("""
    UPDATE users
    SET team = 'Azimi'
    WHERE team IS NULL OR team = '-'
""")
conn.commit()
cur.close()
conn.close()
print('All empty or dash teams set to Azimi.') 