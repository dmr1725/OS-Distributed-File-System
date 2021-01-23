# Contributor: Diego Mendez

# loading in modules
import sqlite3


# creating file path
dbfile = 'C:/Users/diego/Documents/UNI/Fourth Year/CCOM_4017_OS/dfs_skel/dfs.db'
# Create a SQL connection to our SQLite database
con = sqlite3.connect(dbfile)

# creating cursor
cur = con.cursor()

# reading all table names
table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]

dnode = [a for a in cur.execute("Select * from dnode")]
inode = [a for a in cur.execute("Select * from inode")]
block = [a for a in cur.execute("Select * from block")]
# here is you table list
print(table_list)
print(dnode)
print(inode)
print(block)
# Be sure to close the connection
con.close()