#!/usr/bin/env python3
"""
Check database state
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.memory_service import memory_service
from app.config import settings
import pymysql
from urllib.parse import urlparse, parse_qs

def check_database():
    """Check what's in the database"""
    try:
        connection_string = settings.tidb_vector_connection_string
        if connection_string.startswith("mysql+pymysql://"):
            connection_string = connection_string.replace("mysql+pymysql://", "mysql://")
        
        parsed = urlparse(connection_string)
        
        host = parsed.hostname
        port = parsed.port or 3306
        user = parsed.username
        password = parsed.password
        database = parsed.path.lstrip('/')
        
        ssl_params = {}
        if parsed.query:
            query_params = parse_qs(parsed.query)
            if 'ssl_ca' in query_params:
                ssl_params['ssl_ca'] = query_params['ssl_ca'][0]
            if 'ssl_verify_cert' in query_params:
                ssl_params['ssl_verify_cert'] = query_params['ssl_verify_cert'][0] == 'true'
            if 'ssl_verify_identity' in query_params:
                ssl_params['ssl_verify_identity'] = query_params['ssl_verify_identity'][0] == 'true'
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            **ssl_params
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, document, meta FROM mem0 WHERE JSON_EXTRACT(meta, '$.user_id') = 'test_user'")
            results = cursor.fetchall()
            
            print(f"Found {len(results)} records for user 'test_user':")
            for row in results:
                print(f"ID: {row[0]}")
                print(f"Document: {row[1]}")
                print(f"Meta: {row[2]}")
                print("---")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"Database check error: {e}")
        return False

if __name__ == "__main__":
    check_database()