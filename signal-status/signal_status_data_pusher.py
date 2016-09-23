#  status duration enabled
#  enable request verification
#  append new intersections to historical dataset?

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import pymssql
import pyodbc
import arrow
import requests
import json
import email_alert
import sys
from secrets import KITS_CREDENTIALS
from secrets import SOCRATA_CREDENTIALS
from secrets import ALERTS_DISTRIBUTION
from secrets import IDB_PROD_CREDENTIALS

import pdb

SOCRATA_SIGNAL_STATUS = 'https://data.austintexas.gov/resource/5zpr-dehc.json'
SOCRATA_SIGNAL_STATUS_HISTORICAL = 'https://data.austintexas.gov/resource/x62n-vjpq.json'
SOCRATA_PUB_LOGS = 'https://data.austintexas.gov/resource/n5kp-f8k4.json'

EMAIL_FOOTER = '''
    \n
    This is an automated message generated by Austin Transportation's Arterial Management Division. To unsubscribe, contact john.clary@austintexas.gov.
    '''

then = arrow.now()
logfile_filename = 'logs/signals-on-flash/{}.csv'.format(then.format('YYYY-MM-DD'))



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



def get_int_db_data_as_dict(connection, key):

    print('get intersection database data')

    query = '''
        SELECT *
        FROM GIS_QUERY
        WHERE SIGNAL_STATUS = 1 AND SIGNAL_TYPE = 'TRAFFIC'
    '''

    results = []

    grouped_data = {}

    cursor = connection.cursor()
    
    cursor.execute(query)

    columns = [column[0] for column in cursor.description]
    
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    
    for row in results:
        
        for val in row:

            row[val] = str(row[val])

            if row[val] == 'None':
                row[val] = ''

            if val == key:
                new_key = row[key]

        grouped_data[new_key] = row
    
    return grouped_data



def prep_kits_query(intersection_data):
    print('prep kits query')

    ids = intersection_data.keys()
    
    where = str(tuple(ids))
    
    query  = '''
        SELECT i.INTID as kits_id
            , e.DATETIME as status_datetime
            , e.STATUS as signal_status
            , i.POLLST as poll_status
            , e.OPERATION as operation_state
            , e.PLANID as plan_id
            , i.ASSETNUM as atd_signal_id
            FROM [KITS].[INTERSECTION] i
            LEFT OUTER JOIN [KITS].[INTERSECTIONSTATUS] e
            ON i.[INTID] = e.[INTID]
            WHERE i.ASSETNUM IN {}
            ORDER BY e.DATETIME DESC
    '''.format(where)

    return query



def fetch_kits_data(query):
    print('fetch kits data')

    conn = pymssql.connect(
        server=KITS_CREDENTIALS['server'],
        user=KITS_CREDENTIALS['user'],
        password=KITS_CREDENTIALS['password'],
        database=KITS_CREDENTIALS['database']
    )

    cursor = conn.cursor(as_dict=True)

    cursor.execute(query)  

    return cursor.fetchall()



def reformat_kits_data(dataset):
    print('reformat data')
    
    reformatted_data = []
    
    for row in dataset:        
        formatted_row = {}

        for key in row:
            new_key = str(key)
            new_value = str(row[key])
            formatted_row[new_key] = new_value
        
        reformatted_data.append(formatted_row)

    return reformatted_data



def group_data(dataset, key):
    print('group data')

    grouped_data = {}
    
    for row in dataset:
        new_key = str(row[key])
        grouped_data[new_key] = row

    return grouped_data



def check_for_stale_data(dataset):
    print('check for stale data')

    stale = False

    status_times = []

    for record in dataset:
        if record['status_datetime']:
            compare = arrow.get(record['status_datetime'])
            status_times.append(compare)

    oldest_record =  arrow.get(max(status_times)).replace(tzinfo='US/Central')  #  have to swap TZ info here because the database query is incorrectly storing datetimes as UTC

    delta = arrow.now() - oldest_record

    delta_minutes = delta.seconds/60

    if delta_minutes > 15:  #  if more than 15 minutes have passed since a status update

        stale = True

        subject = 'DATA PROCESSING ALERT: KITS Status Data is {} mintues old'.format(str(delta_minutes))

        body = 'DATA PROCESSING ALERT: KITS intersection status data has not been updated for more than {} minutes.'.format(str(delta_minutes))

        body = body + EMAIL_FOOTER

        email_alert.send_email(ALERTS_DISTRIBUTION, subject, body)

    return stale


def prep_stale_data_log(date_time):
    print('prep stale data log')

    return [ {
        'event': 'signal_status_update',
        'timestamp': date_time.timestamp, 
        'date_time':  date_time.format('YYYY-MM-DD HH:mm:ss'),
        'errors': '1',
        'updated': '',
        'created': '',
        'deleted': '',
        'no_update': '',
        'not_processed': '',
        'response_message': 'WARNING: stale data detected'
    } ]


def merge_data(intersection_data, kits_data):
    print('merge intersection and kits data')

    not_in_kits = []

    count = 0

    kits_source_fields = ['kits_id', 'status_datetime', 'signal_status', 'poll_status', 'operation_state', 'plan_id']
    
    for key in list(intersection_data.keys()):

        if key in kits_data:
            for field in kits_source_fields:
                intersection_data[key][field] = kits_data[key][field]

        else:
            not_in_kits.append(key)
            del intersection_data[key]

    print(str(len(not_in_kits)) + " records not found in kits!")

    return {
        'new_data': intersection_data,
        'not_in_kits': not_in_kits
    }



def fetch_published_data():
    print('fetch published data')
    try:
        res = requests.get(SOCRATA_SIGNAL_STATUS, verify=False)

    except requests.exceptions.HTTPError as e:
        raise e

    return res.json()



def detect_changes(new, old):
    print('detect changes')

    upsert = []  #  see https://dev.socrata.com/publishers/upsert.html
    not_processed = []
    no_update = 0  
    insert = 0
    update= 0
    delete = 0    
    upsert_historical = []

    for record in new:
        lookup = str(new[record]['atd_signal_id'])

        if lookup in old:
            new_status = str(new[record]['signal_status'])
            #   new_status = str(9999)  #  tests

            try:
                old_status = str(old[lookup]['signal_status'])

            except:
                not_processed.append(new[record]['atd_signal_id'])
                continue
            
            if new_status == old_status:
                no_update += 1
            
            else:
                update += 1
                
                new[record]['signal_status_previous'] = old_status
                
                upsert.append(new[record])
                
                record_retired_datetime = arrow.now()
                old[lookup]['record_retired_datetime'] = record_retired_datetime.format('YYYY-MM-DD HH:mm:ss')

                processed_datetime = arrow.get(old[lookup]['processed_datetime']).replace(tzinfo='US/Central')

                delta = record_retired_datetime - processed_datetime
                old[lookup]['status_duration'] = delta.seconds
                
                upsert_historical.append(old[lookup])
            
        else:
            insert += 1
            upsert.append(new[record])

    for record in old:  #  compare socrata to KITS to idenify deleted records
        lookup = old[record]['atd_signal_id']
        
        if lookup not in new:
            delete += 1

            upsert.append({ 
                'atd_signal_id': lookup,
                ':deleted': True
            })

    return { 
        'upsert': upsert,
        'not_processed': not_processed,
        'insert': insert,
        'update': update,
        'no_update':  no_update,
        'delete': delete,
        'upsert_historical': upsert_historical
    }



def prepare_socrata_payload(upsert_data):
    print('prepare socrata payload')

    now = arrow.now()

    for row in upsert_data:
        if (':deleted' not in row.keys()):
            row['processed_datetime']  = now.format('YYYY-MM-DD HH:mm:ss')
            row['record_id'] = '{}_{}'.format(row['atd_signal_id'], str(now.timestamp))
            row['location'] = '({},{})'.format(row['latitude'], row['longitude'])

    return upsert_data



def upsert_open_data(payload, url):
    print('upsert open data ' + url)
    
    try:
        auth = (SOCRATA_CREDENTIALS['user'], SOCRATA_CREDENTIALS['password'])

        json_data = json.dumps(payload)

        res = requests.post(url, data=json_data, auth=auth, verify=False)

    except requests.exceptions.HTTPError as e:
        raise e
    
    return res.json()




def package_log_data(date, changes, response, event):
    print('package logfile data for {}'.format(event))

    timestamp = arrow.now().timestamp

    date = date.format('YYYY-MM-DD HH:mm:ss')

    errors = '0'
    updated = '0'
    created = '0'
    deleted = '0'
    response_message = ''
    no_update = '0'

    if (response):

        if 'error' in response.keys():
            response_message = response['message']
            
            email_alert.send_email(ALERTS_DISTRIBUTION, 'DATA PROCESSING ALERT: Socrata Upload Status Update Failure', response_message + EMAIL_FOOTER)

        else:
            errors = response['Errors']
            updated = response['Rows Updated']
            created = response['Rows Created']
            deleted = response['Rows Deleted']
            response_message = ''

    if changes['no_update']:
        no_update = str(changes['no_update'])

    if changes['not_processed']:
        not_processed = str(changes['not_processed'])

    else:
        not_processed = ''
     
    return [ {
        'event': event,
        'timestamp': timestamp, 
        'date_time':  date,
        'errors': errors ,
        'updated': updated,
        'created': created,
        'deleted': deleted,
        'no_update': no_update,
        'not_processed': not_processed,
        'response_message': response_message
    } ]


    
def main(date_time):
    print('starting stuff now')

    try:       
        conn = connect_int_db(IDB_PROD_CREDENTIALS)

        int_db_data = get_int_db_data_as_dict(conn, 'atd_signal_id')
        
        kits_query = prep_kits_query(int_db_data)

        kits_data = fetch_kits_data(kits_query)

        stale = check_for_stale_data(kits_data)

        if stale:
            stale_data_log = prep_stale_data_log(date_time)
            upsert_open_data(stale_data_log, SOCRATA_PUB_LOGS)
            sys.exit()

        kits_data = reformat_kits_data(kits_data)
        
        kits_data = group_data(kits_data, 'atd_signal_id')

        merge_results = merge_data(int_db_data, kits_data)

        old_data = fetch_published_data()

        old_data = group_data(old_data, 'atd_signal_id')

        change_detection_results = detect_changes(merge_results['new_data'], old_data)
        
        socrata_payload = prepare_socrata_payload(change_detection_results['upsert'])

        if socrata_payload:
            socrata_response = upsert_open_data(socrata_payload, SOCRATA_SIGNAL_STATUS)

        else:
            print('no new status data to upload')
            socrata_response = None

        if change_detection_results['upsert_historical']:
            socrata_response_historical = upsert_open_data(change_detection_results['upsert_historical'], SOCRATA_SIGNAL_STATUS_HISTORICAL)

        else:
            print('no new historical status data to upload')
            socrata_response_historical = None

        status_logfile_data = package_log_data(date_time, change_detection_results, socrata_response, 'signal_status_update')
        logfile_response = upsert_open_data(status_logfile_data, SOCRATA_PUB_LOGS)  #  always log status ETL

        if change_detection_results['upsert_historical']:  #  only logging the historical status ETL when the dataset changes
            historical_logfile_data = package_log_data(date_time, change_detection_results, socrata_response, 'historical_signal_status_update')
            logfile_response = upsert_open_data(historical_logfile_data, SOCRATA_PUB_LOGS)
        
        else: 
            historical_logfile_data = None
        
        return {
            'res': socrata_response,
            'res_historical': socrata_response_historical,
            'payload': socrata_payload,
            'status_logfile': status_logfile_data,
            'historical_logfile': historical_logfile_data,
            'not_in_kits': merge_results['not_in_kits']
        }
    
    except Exception as e:
        print('Failed to process data for {}'.format(date_time))
        print(e)
        email_alert.send_email(ALERTS_DISTRIBUTION, 'DATA PROCESSING ALERT: Signal Status Update Failure', str(e) + EMAIL_FOOTER)
        raise e
 


results = main(then)

print(results['res'])
print('Elapsed time: {}'.format(str(arrow.now() - then)))
