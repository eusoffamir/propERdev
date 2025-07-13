import psycopg2

emails = [
    'azimi.proper@gmail.com',
    'aidihafriz@yahoo.com.my',
    'mike.mb2309@gmail.com',
    'utamasupply@gmail.com',
    'yaakub.proper@gmail.com',
    'azmieproper@gmail.com',
    'hartanahidamanku@gmail.com',
    'shariffah@iyres.gov.my',
    'hilmykwa@gmail.com',
    'lanbina.c@gmail.com',
    'zariena.proper@gmail.com',
    'norazizi@gmail.com',
    'nurayn13@gmail.com',
    'ayohcik.proper@gmail.com',
    'faemsosi96@gmail.com',
    'faizulhakimi@gmail.com',
    'ketwomen85@gmail.com',
]

conn = psycopg2.connect(dbname='propdb', user='propuser', password='proppass123', host='localhost', port='5432')
cur = conn.cursor()
for email in emails:
    cur.execute('UPDATE users SET added_by = %s WHERE email = %s', (4, email))
conn.commit()
cur.close()
conn.close()
print('All specified users have been assigned to Azimi Leader (user_id=4).') 