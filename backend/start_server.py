import os
import sys
import asyncio
import logging

backend_dir = r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\backend'
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

# Patch init_db to not hang on database connection
from app.db import session as db_session
original_init_db = db_session.init_db

async def safe_init_db():
    try:
        await asyncio.wait_for(original_init_db(), timeout=5.0)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Database initialization skipped: {e}")

db_session.init_db = safe_init_db

from app.core.config import settings
import uvicorn

uvicorn.run(
    "app.main:app",
    host=settings.API_HOST,
    port=settings.API_PORT,
    reload=settings.DEBUG,
    log_level=settings.LOG_LEVEL.lower(),
)