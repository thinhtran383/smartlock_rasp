import sqlite3

class DataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect('lockdatabase.db')
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