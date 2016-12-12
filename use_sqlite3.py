import sqlite3

connection = sqlite3.connect("users.sqlite3")

try:
    cur = connection.cursor()
    cur.execute('DROP TABLE IF EXISTS Users ')
    cur.execute('CREATE TABLE Users(username TEXT PRIMARY KEY, password TEXT)')

    cur.execute("INSERT INTO Users (username, password) VALUES('Yolanda', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Bryce', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Loski', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Lvppaooo', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Admin', 'Admin')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Tom', '123')")
    cur.execute("SELECT * FROM Users")

    print cur.fetchall()

    cur.execute("UPDATE Users SET password = 'Admin' WHERE username='Bryce' ")
    cur.execute("SELECT * FROM Users")

    print cur.fetchall()

except Exception, emsg:
    print "[-]Exception: %s" % str(emsg), type(emsg)

connection.commit()
connection.close()