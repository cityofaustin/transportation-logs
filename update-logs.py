from StringIO import StringIO
import arrow
import requests
import csv
import json
import base64
from secrets import GITHUB_USERNAME
from secrets import GITHUB_TOKEN
 
REPO_URL = 'https://api.github.com/repos/cityofaustin/transportation-logs/contents'
DATA_URL = 'https://raw.githubusercontent.com/cityofaustin/transportation-logs/master/'
FIELDNAMES = ['date_time', 'change_detected']
GITHUB_AUTH = (GITHUB_USERNAME, GITHUB_TOKEN)
 
today = arrow.now('America/Chicago')
 
filename_short = today.format('YYYY-MM-DD')
 
filename = 'logs/signals-on-flash/6666-66-66.csv'
#  filename = 'logs/signals-on-flash/{}.csv'.format(date.format('YYYY-MM-DD'))
 
request_url = REPO_URL + filename
 
def fetch_logfile_data(date):
    res = requests.get(DATA_URL + filename)
    return str(res.text)
 
 
def update_logfile_github(file, existing_file, date, fieldnames):
    old_data = StringIO(file)
    reader = csv.reader(old_data, fieldnames, lineterminator='\n')
    
    new_file = StringIO()
    writer = csv.writer(new_file, fieldnames, lineterminator='\n')


    for row in reader:
        writer.writerow(row)
 
    writer.writerow([date.format('YYYY-MM-DD HH:mm:ss'), 'YES'])    
    
    csv_text = StringIO.getvalue(new_file)
    commit_file_github(filename, 'master', csv_text, existing_file, 'Automated commit {}'.format(filename_short))
    
 
 
def url_for_path(path):
    return '{}/{}'.format(REPO_URL, path.strip('/'))
 
 
 
def commit_file_github(path, branch, content, existing_file, message, auth=GITHUB_AUTH):
    print('commit to github')
    url = url_for_path(path)
    encoded_content = base64.b64encode(content)
 
    data = {
        'content': encoded_content,
        'branch': branch,
        'message': message
    }
    
    if existing_file:
        data['sha'] = existing_file

    res = requests.put(url, json=data, auth=auth)
    res.raise_for_status()
 
    return res.json()
 
 
 
def create_logfile(date, fieldnames):
    file = StringIO()
    writer = csv.writer(file, fieldnames, lineterminator='\n')
    writer.writerow(fieldnames)
    writer.writerow([date.format('YYYY-MM-DD HH:mm:ss'), 'YES'])
    return file
 
 
 
def create_logfile_github(date):
    fh = create_logfile(date, FIELDNAMES)
    csv_text = StringIO.getvalue(fh)
    commit_file_github(filename, 'master', csv_text, None, 'Automated commit {}'.format(filename_short))
 
 
def fetch_logfile(date):
    print('Getting data for {}'.format(date, date))
 
    try:
        res = requests.get(request_url)
    
    except requests.exceptions.HTTPError as e:
        raise e
    return res
 
 
 
def log_signal_status_etl(date):
    try:
        response = fetch_logfile(date)
        
        if 'Not Found' in response.text:
            print('create new file')
            create_logfile_github(date, old_data)
 
        else:
            print('update existing file')
            old_file = response.json()['sha']
            old_data = fetch_logfile_data(date)
            update_logfile_github(old_data, old_file, date, FIELDNAMES)
            
    except Exception as e:
        print('Failed to commit data for {}'.format(date))
        print(e)
        raise e
 
 
log_signal_status_etl(today)
