import mysql.connector as db

BASE_QUERY = '''
CREATE TABLE IF NOT EXISTS course_outcome (
    sub_code VARCHAR(11) NOT NULL,
    dept VARCHAR(10) NOT NULL,
    exam VARCHAR(10) NOT NULL,
    batch INT NOT NULL,
    co1 INT,
    co2 INT,
    co3 INT,
    co4 INT,
    co5 INT,
    co6 INT,
    PRIMARY KEY (sub_code, exam, batch)
);
'''

INSERT_QUERY = '''
INSERT INTO course_outcome
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
'''

def DBConnection():
    conn = db.connect(
        host='localhost',
        username='root',
        password='',
        database='co_attainment'
    )
    return conn