#! python3
# Function to get SAP job data from various sources

from os import path
from datetime import datetime
import pandas as pd

today = datetime.today().strftime('%Y-%m-%d')

def get_data(job, source, date = today):
    
    # Get data from https://jobs.sap.com/ using web scraper
    if source == 'scrape':
        from get_jobs import get_jobs
        data = get_jobs(job)
        return pd.DataFrame(data[1:], columns = data[0])
    
    # Get data from RESTful API (Flask) - start webservice before running
    elif source == 'api':
        print('Fetching results...') # display text while downloading
        import requests, json
        job = job.strip().replace(' ', '%20')
        res = requests.get('http://localhost:5000/SAP/api/v1.0/jobs/{}'.format(job))
        data = json.loads(res.text)
        print('Done.')
        print('Found {} results.'.format(len(data) - 1))
        return pd.DataFrame(data[1:], columns = data[0])

    # Get data from MySQL database
    elif source == 'mysql':
        import mysql.connector as sqldb
        # Connection to DB
        job_db = sqldb.connect(
            host = 'localhost',
            user = 'root',
            passwd = '',
            database = 'SAP_jobs'
        )
        cursor = job_db.cursor()
        # Fetch all tables (format: 'job@date') in database
        cursor.execute("SHOW TABLES")
        tables = [table_name for (table_name,) in cursor.fetchall()]
        job_date = job.strip().replace(' ', '_') + '@' + date
        # Fetch new data if not yet in database and more than one day old
        if date == today and job_date not in tables:
            from get_jobs import get_jobs_to_db
            get_jobs_to_db(job)
        elif job_date not in tables:
            raise Exception("No job with this date in the database.")
        return pd.read_sql('SELECT * FROM `{}`'.format(job_date), con = job_db)
    
    # Get data from csv file
    elif source == 'csv':
        filename = '{}.csv'.format(job)
        if path.isfile('./' + filename):
            return pd.read_csv(filename)
        else:
            raise Exception("No such file.")
    
    else:
        raise Exception("Source options are 'scrape', 'api', 'mysql', 'csv'.")