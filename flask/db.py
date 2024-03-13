import MySQLdb
import MySQLdb.cursors

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "",
                           db = "roll",
                           cursorclass=MySQLdb.cursors.DictCursor)
    c = conn.cursor()

    return c, conn