import os

class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'  # Make sure it's 'root'
    MYSQL_PASSWORD = 'samrudhi@2005'  # Your MySQL password
    MYSQL_DB = 'hospital_db'  # Your database name
    MYSQL_CURSORCLASS = 'DictCursor'
    SECRET_KEY = os.urandom(24)
