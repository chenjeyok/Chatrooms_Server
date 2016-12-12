import sqlite3
import Tkinter as tk

# ============= Connect ==============
try:
    connection = sqlite3.connect("users.sqlite3")
    cur = connection.cursor()
except Exception, emsg:
    print "[E01]: %s" % str(emsg)

# ============== Origin ===============
try:
    cur.execute("SELECT * FROM Users")
    print '==========[ORIGIN]=========='
    print 'username\tpassword'
    for user in cur.fetchall():
        print user[0],
        print '\t'+user[1]

except Exception, emsg:
    print "[E02]: %s" % str(emsg)

# ============== UPDATE ===============

try:
    cur.execute('DROP TABLE IF EXISTS Users ')
    cur.execute('CREATE TABLE Users(username TEXT PRIMARY KEY, password TEXT)')

    cur.execute("INSERT INTO Users (username, password) VALUES('Bryce', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Lvppaooo', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Yolanda', '123')")


    cur.execute("INSERT INTO Users (username, password) VALUES('Jon.Snow', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Arya.Stark', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Jamine.Lanister', '123')")

    cur.execute("INSERT INTO Users (username, password) VALUES('Walter.White', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Jessy.Pinkman', '123')")

    cur.execute("INSERT INTO Users (username, password) VALUES('Fiona.Gallagher', '123')")

    cur.execute("INSERT INTO Users (username, password) VALUES('Lorne.Malvo', '123')")
    cur.execute("INSERT INTO Users (username, password) VALUES('Lester.Nyggard', '123')")

    cur.execute("SELECT * FROM Users")
    print '==========[UPDATE]=========='
    print 'username\tpassword'
    for user in cur.fetchall():
        print user[0]+'\t'+user[1]

    # cur.execute("UPDATE Users SET password = 'Admin' WHERE username='Bryce' ")
    # cur.execute("SELECT * FROM Users")

except Exception, emsg:
    print "[E03]: %s" % str(emsg)


# ============== COMMIT ===============
connection.commit()
connection.close()
