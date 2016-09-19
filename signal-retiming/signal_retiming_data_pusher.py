#  enable request verification

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import pymssql
import pyodbc
import arrow
import requests
import json
import email_alert
from secrets import SOCRATA_CREDENTIALS
from secrets import ALERTS_DISTRIBUTION
from secrets import IDB_PROD_CREDENTIALS


import pdb


SOCRATA_SYNC_CORRIDORS = 'https://data.austintexas.gov/resource/efct-8fs9.json'
SOCRATA_RETIMINGS = 'https://data.austintexas.gov/resource/eyaq-uimn.json'
SOCRATA_PUB_LOGS = 'https://data.austintexas.gov/resource/n5kp-f8k4.json'

EMAIL_FOOTER = '''
    \n
    This is an automated message generated by Austin Transportation's Arterial Management Division. To unsubscribe, contact john.clary@austintexas.gov.
    '''
then = arrow.now()



def fetch_published_data(dataset_url):
    print('fetch published data')
    
    auth = (SOCRATA_CREDENTIALS['user'], SOCRATA_CREDENTIALS['password'])

    try:
        res = requests.get(dataset_url, verify=False, auth=auth)

    except requests.exceptions.HTTPError as e:
        raise e

    return res.json()



def connect_int_db(credentials):
    print('connecting to intersection database')

    conn = pyodbc.connect(
        'DRIVER={{SQL Server}};' 
            'SERVER={};'
            'PORT=1433;'
            'DATABASE={};'
            'UID={};'
            'PWD={}'
            .format(
                credentials['server'],
                credentials['database'],
                credentials['user'],
                credentials['password'] 
        ))

    cursor = conn.cursor()
    
    return conn


def get_int_db_data_as_dict(connection, table, key):
    print('get intersection database data')
    
    query = 'SELECT * FROM {}'.format(table)

    results = []

    grouped_data = {}

    cursor = connection.cursor()
    
    cursor.execute(query)

    columns = [column[0] for column in cursor.description]
    columns = [c.lower() for c in columns]  #  database fieldnames are in caps :[

    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    for row in results:  #  sloppy conversion of sql object
        
        for val in row:
            
            try:
                row[val] = str(row[val])

            except (ValueError, TypeError):
                pass
            
            if row[val] == 'None':
                row[val] = ''
        
            try:
                if row[val][-2:] == '.0':
                    row[val] = row[val].replace('.0','')

            except:
                pass

            if val == key:
                new_key = row[key]

        grouped_data[new_key] = row

    return grouped_data



def group_socrata_data(dataset, key):
    print('group socrata data')

    grouped_data = {}
    
    for row in dataset:
        new_key = str(row[key])
        grouped_data[new_key] = row

    return grouped_data




def detect_changes(new, old):
    print('detect changes')
    
    upsert = []  #  see https://dev.socrata.com/publishers/upsert.html
    delete = 0    
    
    for record in new:
        upsert.append(new[record])

    for record in old:
        try:
            lookup = record['id']
        except:
            print record
            
        if lookup not in new:
            delete += 1

            upsert.append({     
                'id': lookup,
                ':deleted': True
            })

    return { 
        'upsert': upsert,
        'delete': delete
    }


def upsert_open_data(payload, url):
    print('upsert open data {}'.format(url))

    try:
        auth = (SOCRATA_CREDENTIALS['user'], SOCRATA_CREDENTIALS['password'])

        json_data = json.dumps(payload)

        res = requests.post(url, data=json_data, auth=auth, verify=False)

    except requests.exceptions.HTTPError as e:
        raise e
    
    return res.json()




def package_log_data(date, response, event):
    print('package logfile data for {}'.format(event))
    
    timestamp = arrow.now().timestamp

    date = date.format('YYYY-MM-DD HH:mm:ss')
   
    if 'error' in response.keys():
        response_message = response['message']
        
        email_alert.send_email(ALERTS_DISTRIBUTION, 'DATA PROCESSING ALERT: Signal Retiming Upload Failure', response_message + EMAIL_FOOTER)

        errors = ''
        updated = ''
        created = ''
        deleted = ''

    else:
        errors = response['Errors']
        updated = response['Rows Updated']
        created = response['Rows Created']
        deleted = response['Rows Deleted']
        response_message = ''

    return [ {
        'event': event,
        'timestamp': timestamp, 
        'date_time':  date,
        'errors': errors ,
        'updated': updated,
        'created': created,
        'deleted': deleted,
        'response_message': response_message
    } ]

    

    
def main(date_time):
    print('starting stuff now')

    try:
       
        conn = connect_int_db(IDB_PROD_CREDENTIALS)

        new_retiming_data = get_int_db_data_as_dict(conn, 'RETIMING_QUERY', 'id')
        new_sync_systems = get_int_db_data_as_dict(conn, 'SYNC_INTERSECTIONS_QUERY', 'id')

        old_retiming_data = fetch_published_data(SOCRATA_RETIMINGS)
        old_sync_systems = fetch_published_data(SOCRATA_SYNC_CORRIDORS)

        retiming_detection_results = detect_changes(new_retiming_data, old_retiming_data)
        sync_systems_results = detect_changes(new_sync_systems, old_sync_systems)

        socrata_response_retiming = upsert_open_data(retiming_detection_results['upsert'], SOCRATA_RETIMINGS)
        socrata_response_sync_systems = upsert_open_data(sync_systems_results['upsert'], SOCRATA_SYNC_CORRIDORS)        

        logfile_retiming = package_log_data(date_time, socrata_response_retiming, 'corridor_retiming_update')
        logfile_sync_systems = package_log_data(date_time, socrata_response_sync_systems, 'sync_corridors_update')

        retiming_logfile_response = upsert_open_data(logfile_retiming, SOCRATA_PUB_LOGS)
        sync_systems_logfile_response = upsert_open_data(logfile_sync_systems, SOCRATA_PUB_LOGS)

        return {
            'res_retiming': socrata_response_retiming,
            'res_sync_systems': socrata_response_sync_systems,
            'logfile_retiming': retiming_logfile_response,
            'logfile_sync_systems': sync_systems_logfile_response
        }
    
    except Exception as e:
        print('Failed to process data for {}'.format(date_time))
        print(e)
        email_alert.send_email(ALERTS_DISTRIBUTION, 'DATA PROCESSING ALERT: Signal Retiming Update Failure', str(e) + EMAIL_FOOTER)
        raise e
 
results = main(then)

print(results['res_retiming'])
print(results['res_sync_systems'])
print('Elapsed time: {}'.format(str(arrow.now() - then)))
