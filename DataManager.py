import sqlite3

class DataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect('/home/thinhtran/smartlock/flask/smart_lock.db')
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
    sql = 'update secure set positionFinger = ? where UserId = ?'
    sqlValues = (1,1,)
    db.executeSql(sql, sqlValues)

deleteUser(1)

rs = db.executeSql('select * from secure', fetchResult=True)


print(rs)