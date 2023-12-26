import getpass
from flask import Flask, render_template, request
import oracledb
import cx_Oracle

# pw = getpass.getpass("Enter password: ")

# connection = oracledb.connect(
#     user="system",
#     password=pw,
#     dsn="localhost/orcl")

# print("Successfully connected to Oracle Database")

#cursor = connection.cursor()

app = Flask(__name__)
table_name = ''
data = []

#cx_Oracle.init_oracle_client(lib_dir="C:/App/db_home/bin")
oracle_connection_string = 'system/Jesudhas123%@localhost:1521/orcl'

connection = cx_Oracle.connect(oracle_connection_string)
cursor = connection.cursor()
query = "SELECT * FROM Products"   
cursor.execute(query)
result = cursor.fetchall()
print(result)