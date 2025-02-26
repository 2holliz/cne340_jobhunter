import mysql.connector
import time
import json
import requests
from datetime import date
import html2text


# Connect to database
# You may need to edit the connect function based on your local settings.#I made a password for my database because it is important to do so. Also make sure MySQL server is running or it will not connect
def connect_to_sql():
    return mysql.connector.connect(
        user='root',
        host='127.0.0.1', 
        database='jobs'
    )

# Create the table structure
def create_tables(cursor):
    # Creates table
    # Must set Title to CHARSET utf8 unicode Source: http://mysql.rjweb.org/doc.php/charcoll.
    # Python is in latin-1 and error (Incorrect string value: '\xE2\x80\xAFAbi...') will occur if Description is not in unicode format due to the json data
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS jobs (
               id INT AUTO_INCREMENT PRIMARY KEY, 
               job_id VARCHAR(50) UNIQUE, 
               company VARCHAR(255), 
               created_at DATE, 
               url TEXT, 
               title TEXT, 
               description TEXT
           );
       ''')


# Query the database.
# You should not need to edit anything in this function
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor


# Add a new job
def add_new_job(cursor, jobdetails):
    company_name = html2text.html2text(jobdetails['company_name'])
    url = html2text.html2text(jobdetails['url'])
    title = html2text.html2text(jobdetails['title'])
    description = html2text.html2text(jobdetails['description'])
    job_id = jobdetails['id']
    created_at = jobdetails['publication_date'][0:10]  # Avoid using 'date' as a variable name

    query = '''
    INSERT INTO jobs (job_id, company, created_at, url, title, description)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (job_id, company_name, created_at, url, title, description))

# Check if new job
def check_if_job_exists(cursor, jobdetails):
    cursor.execute("SELECT 1 FROM jobs WHERE job_id = %s", (jobdetails['id'],))
    return cursor.fetchone() is not None


#Deletes job
#from datetime import datetime, timedelta
#def delete_job(cursor):
   #old_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
   #query_sql(cursor, "DELETE FROM jobs WHERE created_at < %s", (old_date,))
#print("Old jobs deleted.")
#COULD NOT FIGURE OUT


# Grab new jobs from a website, Parses JSON code and inserts the data into a list of dictionaries do not need to edit
def fetch_new_jobs():
    return requests.get("https://remotive.io/api/remote-jobs").json()['jobs']


# Main area of the code. Should not need to edit
def jobhunt(cursor):
    # Fetch jobs from website
    jobpage = fetch_new_jobs()  # Gets API website and holds the json data in it as a list
    # use below print statement to view list in json format
    # print(jobpage)
    add_or_delete_job(jobpage, cursor)


def add_or_delete_job(jobpage, cursor):
    for jobdetails in jobpage:
        if not check_if_job_exists(cursor, jobdetails):
            add_new_job(cursor, jobdetails)

# Setup portion of the program. Take arguments and set up the script
# You should not need to edit anything here.
def main():
    # Important, rest are supporting functions
    # Connect to SQL and get cursor
    conn = connect_to_sql()
    cursor = conn.cursor()
    create_tables(cursor)

    while (1):  # Infinite Loops. Only way to kill it is to crash or manually crash it. We did this as a background process/passive scraper
        jobhunt(cursor)
        time.sleep(21600)  # Sleep for 1h, this is ran every hour because API or web interfaces have request limits. Your reqest will get blocked.


# Sleep does a rough cycle count, system is not entirely accurate
# If you want to test if script works change time.sleep() to 10 seconds and delete your table in MySQL
if __name__ == '__main__':
    main()