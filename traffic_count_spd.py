'''
Transform traffic count files so that they can be
inserted into ArcSDE database
'''
import os
import csv
import pdb
import hashlib
import logging
import traceback
import arrow
import secrets
import email_helpers


now = arrow.now()
now_s = now.format('YYYY_MM_DD')

log_directory = secrets.LOG_DIRECTORY
logfile = '{}/traffic_count_pub_{}.log'.format(log_directory, now_s)
logging.basicConfig(filename=logfile, level=logging.INFO)
logging.info('START SPD AT {}'.format(str(now)))

root_dir = secrets.TRAFFIC_COUNT_TIMEMARK_DIR
out_dir = secrets.TRAFFIC_COUNT_OUTPUT_SPD_DIR
row_id_name = 'ROW_ID'
directions = ['NB', 'EB', 'WB', 'SB']

fieldmap = {
    'Total' : 'COUNT_TOTAL',
    '0 - < 15' : 'SPEED_0_14',
    '15 - < 20' : 'SPEED_15_19',
    '20 - < 25' : 'SPEED_20_24',
    '25 - < 30' : 'SPEED_25_29',
    '30 - < 35' : 'SPEED_30_34',
    '35 - < 40' : 'SPEED_35_39',
    '40 - < 45' : 'SPEED_40_44',
    '45 - < 50' : 'SPEED_45_49',
    '50 - < 55' : 'SPEED_50_54',
    '55 - < 60' : 'SPEED_55_59',
    '60 - < 65' : 'SPEED_60_64',
    '65 - < 70' : 'SPEED_65_69',
    '70 - < 200': 'SPEED_70_200'
}


def getFile(path):
    print(path)
    with open(path, 'r') as in_file:
        data = {'data_file':[], 'site_code':''}

        append_lines = False
        current_channel = ''

        for i, line in enumerate(in_file):
            if len(line) < 5:  #  check for blank lines
                continue

            if i == 0:
                data['data_file'] = line.split(',')[1].replace('\'', '').strip('\n').strip()

            if i == 1: 
                data['site_code'] = line.split(',')[1].replace('\'', '').strip('\n').strip()

            if 'CHANNEL' in line.upper():   
                append_lines = False
                current_channel = line.split(',')[1].replace('\'', '').strip('\n').strip()
                data[current_channel] = []

            if 'Date,Time' in line:
                data['header'] = line
                append_lines = True
            
            if append_lines:
                data[current_channel].append(line)

    return data


def appendKeyVal(rows, key, val):
    for row in rows:
        row[key] = val
    return rows


def parseDateTime(d, t):
    dt = '{} {} {}'.format(d, t, 'US/Central')
    dt = arrow.get(dt, 'M/D/YYYY h:mm A ZZZ')
    return dt.to('utc').format('YYYY-MM-DD HH:mm:SS')


def mapFields(rows, fieldmap):
    mapped = []
    for row in rows:
        new_row = {}
        for field in row.keys():
            if field in fieldmap:
                new_row[fieldmap[field]] = row[field]
            else:
                new_row[field] = row[field]
        mapped.append(new_row)
    return mapped


def createRowIDs(rows, hash_field_name, hash_fields):
    hasher = hashlib.sha1()
    for row in rows:
        in_str = ''.join([row[q] for q in hash_fields])
        hasher.update(in_str.encode('utf-8'))
        row[hash_field_name] = hasher.hexdigest()
    return rows

def main():
    count = 0

    for root, dirs, files in os.walk(root_dir):
        for name in files:
            if 'SPD.CSV' in name.upper() and 'PROCESSED' not in root.upper():

                cls_file = os.path.join(root, name)

                data = getFile(cls_file)
                data_file = data['data_file']
                site_code = data['site_code']
                data['combined'] = []
                for d in directions:
                    if d in data:
                        reader =  csv.DictReader(data[d])
                        rows = [row for row in reader]
                        data[d] = rows
                        data[d] = appendKeyVal(data[d], 'DATA_FILE', data_file)
                        data[d] = appendKeyVal(data[d], 'SITE_CODE', site_code)
                        data[d] = appendKeyVal(data[d], 'SPEED_CHANNEL', d)
                        data['combined'] = data[d] + data['combined']
                
                for row in data['combined']:
                    date = row['Date']
                    time = row['Time']
                    row['SPEED_DATETIME'] = parseDateTime(date, time)
                    del(row['Date'])
                    del(row['Time'])

                data['combined'] = mapFields(data['combined'], fieldmap)
                data['combined'] = createRowIDs(data['combined'], row_id_name, ['SPEED_DATETIME', 'DATA_FILE', 'SPEED_CHANNEL'])

                fieldnames = [key for key in data['combined'][0].keys()]

                out_path = os.path.join(out_dir, 'fme_' + name)
                
                #  write to file
                with open(out_path, 'w', newline='\n') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data['combined'])

                #  move processed file to processed dir
                move_dir = os.path.join(root, 'processed')
                
                if not os.path.exists(move_dir):
                    os.makedirs(move_dir)

                move_file = os.path.join(move_dir, name)
                os.rename(cls_file, move_file)
                count += 1 

            else:
                continue

    logging.info('{} files processed'.format(count))

try:
    main()

except Exception as e:
    error_text = traceback.format_exc()
    logging.error(error_text)
    email_helpers.send_email(secrets.ALERTS_DISTRIBUTION, 'Traffic Count Classification Process Failure', error_text)

logging.info('END AT: {}'.format(arrow.now().format()))
