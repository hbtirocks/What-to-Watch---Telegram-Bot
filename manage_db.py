import sqlite3 as db
from sqlite3 import Error
import os

def create(db_name, typ, tbl_name = '', *data):
    #for database:- typ = 'db' and for table :- typ = 'table'
    #*data only in case of table(col_name TYPE NOT NULL | PRIMARY KEY |DEFAULT etc..)
    conctn = None
    cursr = None
    try:
        if typ == 'db':
            #Checking if database already exists
            if os.path.isfile("database/"+db_name):
                print('Database {0} already exists !'.format(db_name))
                return 0
            #Creating database if not exists
            conctn = db.connect("database\\"+db_name)
            print('Database {0} successfully created !'.format(db_name))
        elif typ == 'table' and tbl_name != '':
            #Checking if table already exists in database.
            conctn = db.connect("database\\"+db_name)
            cursr = conctn.cursor()
            cursr.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';")
            rows = cursr.fetchall()
            for row in rows:
                if row[0] == tbl_name:
                    print('Table {0} already existed in {1} database'.format(tbl_name, db_name))
                    return 0

            #Creating table if not exists in database.    
            qry = "CREATE TABLE IF NOT EXISTS {0}(".format(tbl_name)
            for i in range(len(data)-1):
                qry += "{0}, ".format(data[i])
            qry += "{0});".format(data[len(data)-1])
            cursr.execute(qry)
            print('Table {0} successfully created in {1} database'.format(tbl_name, db_name))
            
    except Error as e:
        print(e)
        
    finally:
        if cursr:
            cursr.close()
        if conctn:
            conctn.close()
        
       

def write_table(db_name, tbl_name, qry, **data):
    #db_name :- Name of database to be queried in
    #tbl_name :- Name of table in db to be queried upon
    #qry :- Type of query i.e. 'INSERT', 'UPDATE', 'DELETE'
    #**data format
    #for qry type 'INSERT'
    #values = [(a,b,c,d) ,(p,q,r,s), (_,_,_,_)]
    #for qry type 'UPDATE'
    #update = [col1, col2, col3], where = [col4, 'and/or..', col5], values = [(a,b,c,d,e) ,(p,q,r,s,t), (_,_,_,_,_)]
    #for qry type 'DELETE'
    #where = [col4, 'and/or..', col5], values = [(a,b) ,(p,q), (_,_)]
    conctn = None
    try:
        #Checking if database already exists
        if os.path.isfile("database/"+db_name):
            conctn = db.connect("database\\"+db_name)
        else:
            print("sorry ! {0} do not exist".format(db_name))
            return 0
        
        cursr = conctn.cursor()
        #Creates a cursor object with alreday established connection to db

        cursr.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';")
        rows = cursr.fetchall()
        for row in rows:
            if row[0] == tbl_name:
                if qry.upper() == 'INSERT':
                    cursr.execute("SELECT COUNT(*) FROM pragma_table_info('{0}');".format(tbl_name))
                    col = cursr.fetchall()
                    col = col[0][0]
                    qry = "INSERT INTO {0} VALUES(".format(tbl_name)
                    for i in range(col-1):
                        qry += "?, "
                    qry += "?);"
                    cursr.executemany(qry, data['values'])
                    print("Data in {0} inserted successfully!".format(tbl_name))
                    conctn.commit()
                    #Python supports manual commit by default., Means any change like
                    #INSERT, UPDATE, DELETE etc. will reflect only after commiting
                    #Otherwise changes will loose after execution of script
                elif qry.upper() == 'UPDATE':
                    qry = "UPDATE {0} SET ".format(tbl_name)
                    for i in range(len(data['update'])-1):
                        qry += "{0} = ?, ".format(data['update'][i])
                    qry += "{0} = ?".format(data['update'][len(data['update'])-1])

                    if data.get('where'):
                        qry += " WHERE "
                        for i in range(0, len(data['where'])-1, 2):
                            qry += "{0} = ? {1} ".format(data['where'][i], data['where'][i+1])
                        qry += "{0} = ?".format(data['where'][len(data['where'])-1])
                        
                    qry += ";"
                    
                    if data.get('where'):
                        cursr.executemany(qry, data['values'])
                    else:
                        cursr.execute(qry)
                        
                    print("Data in {0} updated successfully!".format(tbl_name))
                    conctn.commit()
                elif qry.upper() == 'DELETE':
                    qry = "DELETE FROM {0}".format(tbl_name)

                    if data.get('where'):
                        qry += " WHERE "
                        for i in range(0, len(data['where'])-1, 2):
                            qry += "{0} = ? {1} ".format(data['where'][i], data['where'][i+1])
                        qry += "{0} = ?".format(data['where'][len(data['where'])-1])
                        
                    qry += ";"
                    
                    if data.get('where'):
                        cursr.executemany(qry, data['values'])
                    else:
                        cursr.execute(qry)
                        
                    print("Data from {0} deleted successfully!".format(tbl_name))
                    conctn.commit()   
                break
            else:
                print("Table {0} do not exist in {1}".format(db_name, tbl_name))
    except Error as e:
        print(e)
    finally:
        if conctn:
            cursr.close()
            conctn.close()
            #finally closing the connection to db.
            print('Connection to database is closed')

def read_table(db_name, tbl_name, **data):
    conctn = None
    rows = None
    try:
        #Checking if database already exists
        if os.path.isfile("database/"+db_name):
            conctn = db.connect("database\\"+db_name)
        else:
            print("sorry ! {0} do not exist".format(db_name))
            return 0
        
        cursr = conctn.cursor()
        #Creates a cursor object with alreday established connection to db

        cursr.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';")
        rows = cursr.fetchall()
        for row in rows:
            if row[0] == tbl_name:
                qry = "SELECT "
                for i in range(len(data['select'])-1):
                    qry += "{0}, ".format(data['select'][i])
                qry += "{0}".format(data['select'][len(data['select'])-1])

                qry += " FROM {0}".format(tbl_name)
                
                if data.get('where'):
                    qry += " WHERE "
                    for i in range(0, len(data['where'])-1, 2):
                        qry += "{0} = ? {1} ".format(data['where'][i], data['where'][i+1])
                    qry += "{0} = ?".format(data['where'][len(data['where'])-1])

                qry += ";"

                if data.get('where'):
                    cursr.execute(qry, data['values'])
                else:
                    cursr.execute(qry)
                rows = cursr.fetchall()
                break
            else:
                print("Table {0} do not exist in {1}".format(db_name, tbl_name))
    except Error as e:
        print(e)
    finally:
        if conctn:
            cursr.close()
            conctn.close()
            #finally closing the connection to db.
            print('Connection to database is closed')
            return rows
                
                            
#Table :- movie_info
#columns :- chat_id (INT), message_id (INT), id (INT), name (TEXT), year (TEXT), category(Text), poster(Text)
print(read_table('movie_info.db', 'chat_info', select=['*']))

