from fastapi import FastAPI
from db.connection import start_db_connections

app = FastAPI()

start_db_connections()