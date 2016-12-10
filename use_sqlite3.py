import sqlite3

connection = sqlite3.connect("music.sqlite3")

try:
    cur = connection.cursor()
    cur.execute(ur'DROP TABLE IF EXISTS Tracks ')
    cur.execute(ur'CREATE TABLE Tracks(title TEXT, plays INTEGER)')

    cur.execute(ur"INSERT INTO Tracks (title, plays) VALUES('My Way', 15)")
    cur.execute(ur"INSERT INTO Tracks (title, plays) VALUES('Road To West', 23), ('Remix It', 16)")

    cur.execute(ur"SELECT * FROM Tracks WHERE plays >= 15")
    print cur.fetchall()

    cur.execute(ur"UPDATE Tracks SET plays=plays+100 WHERE title='My Way'")
    cur.execute(ur"SELECT * FROM Tracks")
    print cur.fetchall()

except Exception, emsg:
    print "[-]Exception: %s" % str(emsg), type(emsg)

connection.commit()
connection.close()

