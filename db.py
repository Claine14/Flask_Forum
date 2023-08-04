import pymysql


def db_connection():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        database='Tugas_forum_pdt',
        user='root',
        password=''
    )
    return conn
