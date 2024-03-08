import sqlite3

from datetime import datetime, timedelta

class DataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect('/home/thinhtran/smartlock/smart_lock.db')
            cls._instance.cursor = cls._instance.conn.cursor()
        return cls._instance
    
    def executeSql(self, sql, values=None, fetchResult=False):
        try:
            if values:
                self.cursor.execute(sql, values)
            else:
                self.cursor.execute(sql)
            
            if fetchResult:
                return self.cursor.fetchall()
            else:
                self.conn.commit()
        except sqlite3.Error as e:
            print('SQLite err: ', e)
            return None
        

db = DataManager()

def deleteUser(passcode):
    
    tw = datetime.now() - timedelta(days=1)
    print(tw)
    sql_update = 'update history set time = ? where userId = ?'
    sqlValues = (tw,3,)
    db.executeSql(sql_update, sqlValues)

deleteUser(1)


'''
sql = 'select root from secure where passcode = ?'
sql_values = ('000000',)
rs = db.executeSql(sql, sql_values, fetchResult=True)

if rs:
    print('root')
'''
