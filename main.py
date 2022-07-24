from application import app
import sqlite3
from sqlite3 import Error


db = None
try:
    db = sqlite3.connect("hms.db")
    db.execute(
        "create table if not exists users(id integer primary key ,firstname text,lastname text,username text,email text,password text,accid text)"
    )

except Error as e:
    print(e)

db.close()
