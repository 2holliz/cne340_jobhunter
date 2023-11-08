import mysql.connector
import time
import json
import requests
from datetime import datetime, timedelta
import html2text


# Connect to database
# You may need to edit the connect function based on your local settings.#I made a password for my database because it is important to do so. Also make sure MySQL server is running or it will not connect
def connect_to_sql():
    conn = mysql.connector.connect(user='root', host='127.0.0.1', database='jobhunter')
    return conn


# Create the table structure
def create_tables(cursor):
    # Creates table
    # Must set Title to CHARSET utf8 unicode Source: http://mysql.rjweb.org/doc.php/charcoll.
    # Python is in latin-1 and error (Incorrect string value: '\xE2\x80\xAFAbi...') will occur if Description is not in unicode format due to the json data
    # I didn't have to make any modifications when making the table and my titles are showing up fine.
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (id INT PRIMARY KEY auto_increment, Job_id varchar(50) , 
        company varchar (300), Created_at DATE, url varchar(30000), Title LONGBLOB, Description LONGBLOB ); ''')

# Query the database.
# You should not need to edit anything in this function
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor


# Add a new job
def add_new_job(cursor, jobdetails):
    # extract all required columns
    # Assign extracted details to variables to insert into the table
    Job_id = str(jobdetails['id'])
    company = html2text.html2text(jobdetails['company_name'])
    title = html2text.html2text(jobdetails['title'])
    url = html2text.html2text(jobdetails['url'])
    description = html2text.html2text(jobdetails['description'])
    date = jobdetails['publication_date'][0:10]
    # Insert statement
    query = cursor.execute("INSERT INTO jobs(Job_id, company, title, url, Description, Created_at " ") "
               "VALUES(%s,%s,%s,%s,%s,%s)", (Job_id, company, title, url,  description, date))
     # %s is what is needed for Mysqlconnector as SQLite3 uses ? the Mysqlconnector uses %s
    return query_sql(cursor, query)

# Should replace with a more effective notification method such as email or messaging service if there is time
def notify_user(jobdetails):
    print(f"New job posting found: {jobdetails['title']} at {jobdetails['company_name']}")
    print(f"URL: {jobdetails['url']}")

# Check if new job
def check_if_job_exists(cursor, jobdetails):
    # Matches the id from the jobdetails variable to the Job_id in the table to determine if the job already exists. This should prevent duplicates from being created
    query = 'SELECT * FROM jobs WHERE Job_id = %s'
    cursor.execute(query, (jobdetails['id'],))
    exists = cursor.fetchone()
    if exists:
        return True
    else:
        return False

# Deletes job
def delete_job(cursor, jobdetails):
    ##Add your code here
    query = "UPDATE"
    return query_sql(cursor, query)


# Grab new jobs from a website, Parses JSON code and inserts the data into a list of dictionaries do not need to edit
def fetch_new_jobs():
    query = requests.get("https://remotive.io/api/remote-jobs")
    datas = json.loads(query.text)
#    print(datas)
    return datas


# Main area of the code. Should not need to edit
def jobhunt(cursor):
    # Fetch jobs from website
    jobpage = fetch_new_jobs()  # Gets API website and holds the json data in it as a list
    # use below print statement to view list in json format
#    print(jobpage)
    add_or_delete_job(jobpage, cursor)


def add_or_delete_job(jobpage, cursor):
    # Add your code here to parse the job page
    for jobdetails in jobpage['jobs']:  # EXTRACTS EACH JOB FROM THE JOB LIST. It errored out until I specified jobs. This is because it needs to look at the jobs dictionary from the API. https://careerkarma.com/blog/python-typeerror-int-object-is-not-iterable/
#        print(jobdetails) # Print statement to see what the current output looks like and to help identify keys
        # Add in your code here to check if the job already exists in the DB
        exists = check_if_job_exists(cursor, jobdetails)
#        is_job_found = len(cursor.fetchall()) > 0  # https://stackoverflow.com/questions/2511679/python-number-of-rows-affected-by-cursor-executeselect
        # Uses boolean value returned by check_if_job_exists to determine if the job is in the table already or not.
        if exists == True:
            pass
        else:
            # INSERT JOB
            add_new_job(cursor, jobdetails)
            # Add in your code here to notify the user of a new posting. This code will notify the new user
            notify_user(jobdetails)

    # Queries to make sure I can pull any data I might need from the database
    cursor.execute("SELECT * FROM jobs WHERE title LIKE '%Engineer%'")
    full_stack = cursor.fetchall()
    print(full_stack)
    cursor.execute("SELECT * FROM jobs WHERE Created_at = '2023-11-07'")
    specific_date = cursor.fetchall()
    print(specific_date)

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
        conn.commit()
        time.sleep(14400)  # Sleep for 1h, this is ran every hour because API or web interfaces have request limits. Your reqest will get blocked.


# Sleep does a rough cycle count, system is not entirely accurate
# If you want to test if script works change time.sleep() to 10 seconds and delete your table in MySQL
if __name__ == '__main__':
    main()

