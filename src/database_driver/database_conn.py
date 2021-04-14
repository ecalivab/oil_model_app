from configparser import ConfigParser
import psycopg2
import psycopg2.extras as extras
import pandas as pd
from psycopg2 import sql
from typing import Tuple

#CWD = /home/caliva/Documents/GeoPandas/src/

def config(filename='database_driver/database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    print("Connection successful")

    return conn

def close_conn(conn):
    if conn is not None:
        conn.close()
        print("Database Connection close.")

def insert_into(conn, table_name, dataframe):
    """
    Using psycopg2.extras.execute_values() to insert the dataframe
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in dataframe.to_numpy()] #To index a tuple of values there should be tuples (12.5,) or a list [12.5]
    # Comma-separated dataframe columns
    cols = ','.join(list(dataframe.columns))
    # SQL query to execute
    query  = "INSERT INTO %s(%s) VALUES %%s" % (table_name, cols)
    
    cursor = conn.cursor()
    
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_values() done")
    cursor.close()

def get_values (conn, table_name, values='*' ,where=None) -> Tuple[pd.DataFrame, int]:
    cursor = conn.cursor()
    
    query  = """SELECT %s FROM %s""" % (values, table_name)

    if where is not None:
        query  = """SELECT %s FROM %s WHERE %s""" % (values, table_name, where) #Condition='cond'

    try:
        cursor.execute(query)
        count = cursor.rowcount
        records = cursor.fetchall()

        # Extract the column names
        col_names = []
        for element in cursor.description:
            col_names.append(element[0])

        # Create the dataframe, passing in the list of col_names extracted from the description
        df = pd.DataFrame(records, columns=col_names)
        return df, count

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
    cursor.close()

def get_values_simple (conn, table_name, values=None,where=None) -> pd.DataFrame:
    cursor = conn.cursor()

    if values is not None:
        query  = sql.SQL(
            """SELECT {values} 
            FROM {table_name}""").format(values=sql.SQL(",").join(map(sql.Identifier, values)), table_name= sql.Identifier(table_name),)
        where_val = None         

        if where is not None:
            where_str = where.split("=")
            where_val = where_str[1]
            query  = sql.SQL(
                """SELECT {values} FROM {table_name} WHERE {key}=%s""").format(
                                                                            values=sql.SQL(",").join(map(sql.Identifier, values)), 
                                                                            table_name=sql.Identifier(table_name),
                                                                            key=sql.Identifier(where_str[0]),)
    else:
        if where is not None:
            where_str = where.split("=")
            where_val = where_str[1]
            query  = sql.SQL(
                """SELECT * FROM {table_name} WHERE {key}=%s""").format(table_name=sql.Identifier(table_name), key=sql.Identifier(where_str[0]),)
              
        else:
            query  = sql.SQL(
                """SELECT * FROM {table_name}""").format(table_name= sql.Identifier(table_name),)
            where_val = None  

    try:
        cursor.execute(query ,(where_val,))
        records = cursor.fetchall()

        # Extract the column names
        col_names = []
        for element in cursor.description:
            col_names.append(element[0])

        # Create the dataframe, passing in the list of col_names extracted from the description
        df = pd.DataFrame(records, columns=col_names)
        return df

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
    cursor.close()


if __name__ == '__main__':
    conn = connect()
    close_conn(conn)
