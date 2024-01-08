'''import sqlite3

conn = sqlite3.connect('lockdatabase.db')

cursor = conn.cursor()

cursor.execute('select * from user_data')
rows = cursor.fetchall()

for row in rows:
    print(row)
    
conn.close()
'''


from DataManager import DataManager
db = DataManager()


selectSql = 'select * from user_data'

result = db.executeSql(selectSql, fetchResult=True)

print(result)

'''
insert= 'Insert into user_data (passcode) values (?)'
insertValues = ('3897',)
db.executeSql(insert, insertValues)'''


'''
import sqlite3

conn = sqlite3.connect('lockdatabase.db')
cursor = conn.cursor()

alterSql = 'update user_data set root = 1 where passcode = \'3897\''
cursor.execute(alterSql)

conn.commit()
conn.close()
'''