import sqlite3


# Kết nối đến cơ sở dữ liệu (nếu không tồn tại, sẽ tự động tạo mới)
conn = sqlite3.connect('/home/thinhtran/smartlock/flask/smart_lock.db')

# Tạo đối tượng cursor để thực hiện các truy vấn SQL
cursor = conn.cursor()

# Tạo bảng Users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        userId INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) NOT NULL
    )
''')



# Tạo bảng History với tùy chọn ON DELETE NO ACTION
cursor.execute('''
    CREATE TABLE IF NOT EXISTS History (
        historyId INTEGER PRIMARY KEY AUTOINCREMENT,
        userId INTEGER,
        time DATETIME NOT NULL,
        FOREIGN KEY (userId) REFERENCES Users (userId) ON DELETE NO ACTION
    )
''')

# Tạo bảng secures
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Secures (
        secureId INTEGER PRIMARY KEY AUTOINCREMENT,
        passcode VARCHAR(50) NOT NULL,
        positionFinger VARCHAR(50),
        accessCount int DEFAULT 0,
        temporaryPasscode TINYINT(1) DEFAULT 0,
        userId INTEGER,
        root TINYINT(1) DEFAULT 0,
        FOREIGN KEY (userId) REFERENCES Users (userId)
    )
''')

# Tạo index cho bảng History
cursor.execute('CREATE INDEX IF NOT EXISTS idx_userId_history ON History (userId)')

# Tạo index cho bảng secures
cursor.execute('CREATE INDEX IF NOT EXISTS idx_userId_secures ON secures (userId)')

# Lưu các thay đổi và đóng kết nối
conn.commit()
conn.close()

