import mysql.connector
from config import *

conn=mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)

cursor=conn.cursor(dictionary=True)