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


selectSql = 'drop table if exists user_data'

create = '''
    create table user_data(
        id integer primary key autoincrement,
        passcode text,
        finger text default null,
        root boolean default 0
    )
'''
insert = 'insert into user_data(passcode,root) values(?,?)'
values = ('3897','1')

select = 'select finger from user_data where passcode = \'3897\' '

selectAll = 'select * from user_data'

result = db.executeSql(selectAll, fetchResult=True)

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