import sqlite3

conn = sqlite3.connect('api.db')
print "Opened database successfully";

conn.execute('drop table if exists User')#
conn.execute('CREATE TABLE IF NOT EXISTS User(Password TEXT, PhoneNumber INTEGER,accessKey TEXT, accessToken TEXT)')
print "Table user ok"

conn.execute('drop table if exists Files')#
conn.execute('CREATE TABLE IF NOT EXISTS Files(accessKey TEXT, fileName TEXT, fileType TEXT)')
print "Table files ok"

conn.close()