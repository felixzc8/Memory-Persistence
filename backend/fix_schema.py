#!/usr/bin/env python3
"""
Fix database schema by dropping and recreating tables.
This will remove the incorrect 'messages' column from the sessions table.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine
from app.db.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_schema():
    """Drop and recreate all tables with correct schema"""
    try:
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Creating tables with correct schema...")
        Base.metadata.create_all(bind=engine)
        logger.info("Schema fixed successfully!")
    except Exception as e:
        logger.error(f"Error fixing schema: {e}")
        raise

if __name__ == "__main__":
    fix_schema()