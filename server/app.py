from contextlib import contextmanager
from fastapi import FastAPI

from db.connection import start_db_connections, stop_db_connections
from .api.product import router as product_router

app = FastAPI()

app.include_router(product_router)

@app.on_event('startup')
def startup_event():
    start_db_connections()


@app.on_event('shutdown')
def shutdown_event():
    stop_db_connections()