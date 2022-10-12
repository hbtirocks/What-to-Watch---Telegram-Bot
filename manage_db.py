import sqlite3 as db

def start_connection(db_name):
    try:
        conctn = db.connect('database\\'+db_name)
        #Creates, if not exists, a db in the databse folder of current directory
        #and return the connection object to this db
    except:
        print(db.Error())

    return conctn

def write_table(db_name, tbl_name, qry, **data):
    try:
        temp_con = db.connect('database\master_info.db')
        temp_cur = conctn.cursor()
        temp_cur.execute("SELECT db_name FROM db_info")
        rows = temp_cur.fetchall()
        for row in rows:
            if row[0][0] == db_name:
                conctn = db.connect('databse\\'+db_name)
                print('Connection established successfully with {0}'.format(db_name))
                break
        temp_cur.close()
        temp_con.close()
    except:
        print(db.Error())
        
    try:
        cursr = conctn.cursor()
        #Creates a cursor object with alreday established connection to db

        cursr.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';")
        rows = cursr.fetchall()
        for row in rows:
            if row[0][0] == tbl_name:
                if qry == 'INSERT':
                    cursr.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{0}'".format(tbl_name))
                    col = cursr.fetchall()
                    col = col[0][0]
                    qry = "INSERT INTO {0} VALUES(".format(tbl_name)
                    for i in range(col-1):
                        qry += "?, "
                    qry += "?);"
                    
                    
                
                break
        
        cursr.execute(table_comnd)
        #executing various queries in connected db.
        
        conctn.commit()
        #Python supports manual commit by default., Means any change like
        #INSERT, UPDATE, DELETE etc. will reflect only after commiting
        #Otherwise changes will loose after execution of script
        
        #execute a command for cr
        #cursr.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';")
        cursr.execute("SELECT * FROM db_info")
        #execute a command for fetching all table names from connected db
        print(cursr.fetchall())
    except:
        print(db.Error())
    finally:
        if conctn:
            cursr.close()
            conctn.close()
            #finally closing the connection to db.
            print('Connection to database is closed')"""

        
c1 = "CREATE TABLE IF NOT EXISTS db_info(db_name TEXT NOT NULL)"
c2 = """INSERT INTO db_info(db_name)
VALUES('movie_info.db');"""

write_table(start_connection('master_info.db'), c2)

