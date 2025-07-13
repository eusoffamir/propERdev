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
    SET nric = regexp_replace(nric, '\\.0$', '')
    WHERE nric LIKE '%.0'
""")
conn.commit()
cur.close()
conn.close()
print('NRIC .0 removed from all users.') 