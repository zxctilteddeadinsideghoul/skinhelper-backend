from contextlib import contextmanager
from fastapi import FastAPI

from db.connection import start_db_connections, stop_db_connections
from .api import (
    product_router,
    brand_router,
    category_router,
    ingredient_router,
    skin_type_router,
    concern_router,
    tag_router,
)

app = FastAPI()

# Register all routers
app.include_router(product_router)
app.include_router(brand_router)
app.include_router(category_router)
app.include_router(ingredient_router)
app.include_router(skin_type_router)
app.include_router(concern_router)
app.include_router(tag_router)

@app.on_event('startup')
def startup_event():
    start_db_connections()


@app.on_event('shutdown')
def shutdown_event():
    stop_db_connections()