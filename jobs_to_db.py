#! python3

import mysql.connector as sqldb
from datetime import datetime

job_db = sqldb.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    database = 'SAP_jobs'
)

cursor = job_db.cursor()

def create_table(string):
    string = '`' + string + '`'
    query = """
    CREATE TABLE {} (
        `Job Title` VARCHAR(255),
        `Date Posted` DATE,
        `Location` VARCHAR(255),
        `Requisition ID` INT,
        `Expected Travel` VARCHAR(255),
        `Career Status` VARCHAR(255),
        `Employment Type` VARCHAR(255),
        `Requirements` TEXT,
        PRIMARY KEY (`Requisition ID`)
    )
    ENGINE = InnoDB;
    """
    cursor.execute(query.format(string))

def insert_row(table, row):
    table = '`' + table + '`'
    row[1] = datetime.strptime(row[1], '%b %d, %Y').strftime('%Y-%m-%d')
    row[-1] = row[-1].replace("'", "''")
    values = ', '.join(["'" + i + "'" for i in row])
    #print(values)
    query = """
    INSERT INTO {} (
        `Job Title`,
        `Date Posted`,
        `Location`,
        `Requisition ID`,
        `Expected Travel`,
        `Career Status`,
        `Employment Type`,
        `Requirements`)
        VALUES ({})
    """
    cursor.execute(query.format(table, values))
    job_db.commit()