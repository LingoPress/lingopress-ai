import psycopg2

import os
from dotenv import load_dotenv

# load .env
load_dotenv()

db_host = os.environ.get('DB_HOST')
db_dbname = os.environ.get('DB_DBNAME')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_port = os.environ.get('DB_PORT')


class Databases:
    def __init__(self):
        self.db = psycopg2.connect(host=db_host, dbname=db_dbname, user=db_user,
                                   password=db_password, port=db_port)
        self.cursor = self.db.cursor()
        print('DB 연결 성공')

    def __del__(self):
        self.db.close()
        if self.cursor:
            self.cursor.close()

    def execute(self, query, args=None):
        if args is None:
            args = {}
        try:
            self.cursor.execute(query, args)
            return self.cursor.fetchall()
        except Exception as e:
            print("Query 실행 에러: ", e)
            return None
        finally:
            self.db.commit()

    def commit(self):
        self.db.commit()
