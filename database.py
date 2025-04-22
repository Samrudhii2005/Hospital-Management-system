import MySQLdb

# ✅ Connect to MySQL
db = MySQLdb.connect(host="localhost", user="samru", passwd="samrudhi@2005")
cursor = db.cursor()

# ✅ Create Database
cursor.execute("CREATE DATABASE IF NOT EXISTS hospital")
cursor.execute("USE hospital")

# ✅ Create Users Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role ENUM('admin', 'doctor', 'patient') NOT NULL
    )
""")

db.commit()
db.close()

print("✅ Database and tables created successfully!")
