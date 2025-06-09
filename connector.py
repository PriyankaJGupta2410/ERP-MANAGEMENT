import pymysql
import os
from dotenv import load_dotenv
from pymysql.cursors import DictCursor

load_dotenv()

####################### MySQL CREDENTIALS ######################
HOST = os.environ.get("DB_HOST")
DBNAME = os.environ.get("DB_NAME")
PASSWORD = os.environ.get("DB_PASSWORD")
USER = os.environ.get("DB_USER")
conn = pymysql.connect(host=HOST,user=USER,password=PASSWORD,database=DBNAME,cursorclass=DictCursor)

db = conn.cursor()