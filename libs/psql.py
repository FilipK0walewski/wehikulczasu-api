import os
from dotenv import load_dotenv
from databases import Database

load_dotenv()

psql_conn_string = os.getenv('PSQL_CONN_STRING')
print(psql_conn_string)
db = Database(psql_conn_string)