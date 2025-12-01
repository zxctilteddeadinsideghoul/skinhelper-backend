#!/bin/sh
alembic upgrade head
uvicorn server.app:app --host 0.0.0.0 --port 8000
