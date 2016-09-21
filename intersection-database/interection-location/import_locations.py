import pyodbc
import csv
from secrets import IDB_PROD_CREDENTIALS

import pdb

SOURCE_FILE = 'source-data/INTERSECTION_LOCATION_ID_IMPORT.csv'

wait = 'N'

while wait != 'Y':
    wait = raw_input('You are about to make changes to a production database. Press \'Y\' to continue.')
    wait = wait.upper()

def connect_db():
    print('connecting to db')

    conn = pyodbc.connect(
        'DRIVER={{SQL Server}};' 
            'SERVER={};'
            'PORT=1433;'
            'DATABASE={};'
            'UID={};'
            'PWD={}'
            .format(
                IDB_PROD_CREDENTIALS['server'],
                IDB_PROD_CREDENTIALS['database'],
                IDB_PROD_CREDENTIALS['user'],
                IDB_PROD_CREDENTIALS['password'] 
        ))

    return conn

def get_csv_data(source_file):
    print('getting csv data')

    with open(source_file, 'r') as file:
        reader = csv.DictReader(file)
        reader = [row for row in reader]
        return reader

def update_database(connection, payload, table):
    print('updating {} records in database'.format(str(len(payload))))

    updated = 0

    cursor = connection.cursor()

    for record in payload:

        statement = '''
            UPDATE {} 
            SET ATD_LOCATION_ID={ATD_LOCATION_ID}
            WHERE ID={ID} 
        '''.format(table, **record)

        print(statement)

        cursor.execute(statement)

        connection.commit()

        updated += 1

    return updated

conn = connect_db()

csv_data = get_csv_data(SOURCE_FILE)

results = update_database(conn, csv_data, 'Access.INTERSECTION')

print('{} records updated'.format(str(results)))
