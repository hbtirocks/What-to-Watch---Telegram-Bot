import sqlite3 as db

def start_connection(db_name):
    try:
        conctn = db.connect('database\\'+db_name)
        #Creates, if not exists, a db in the databse folder of current directory
        #and return the connection object to this db
    except:
        print(db.Error())

    return conctn

def create_table(conctn, table_comnd):
    try:
        cursr = conctn.cursor()
        #Creates a cursor object with alreday established connection to db 
        cursr.execute(table_comnd)
        #execute a command for creating a table in connected db
        cursr.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';")
        ##execute a command for fetching all table names from connected db
        print(cursr.fetchall())
    except:
        print(db.Error())
    finally:
        if conctn:
            conctn.close()
            #finally closing the connection to db.
            print('Connection to database is closed')

table_comnd = """CREATE TABLE IF NOT EXISTS chat_info(
chat_id INTEGER NOT NULL,
message_id INTEGER NOT NULL,
id INTEGER NOT NULL,
name TEXT NOT NULL,
year INTEGER DEFAULT '',
category TEXT DEFAULT '',
poster TEXT DEFAULT '');"""

create_table(start_connection('movie_info.db'), table_comnd)


