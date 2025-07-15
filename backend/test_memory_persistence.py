#!/usr/bin/env python3
"""
Test script to reproduce the erroneous memory deletion issue
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.memory_service import memory_service
from app.config import settings
import pymysql
from urllib.parse import urlparse, parse_qs
import json

def check_database_for_user(user_id):
    """Check what's in the database for a specific user"""
    try:
        # Parse connection string
        connection_string = settings.tidb_vector_connection_string
        if connection_string.startswith("mysql+pymysql://"):
            connection_string = connection_string.replace("mysql+pymysql://", "mysql://")
        
        parsed = urlparse(connection_string)
        
        host = parsed.hostname
        port = parsed.port or 3306
        user = parsed.username
        password = parsed.password
        database = parsed.path.lstrip('/')
        
        # Parse SSL params
        ssl_params = {}
        if parsed.query:
            query_params = parse_qs(parsed.query)
            if 'ssl_ca' in query_params:
                ssl_params['ssl_ca'] = query_params['ssl_ca'][0]
            if 'ssl_verify_cert' in query_params:
                ssl_params['ssl_verify_cert'] = query_params['ssl_verify_cert'][0] == 'true'
            if 'ssl_verify_identity' in query_params:
                ssl_params['ssl_verify_identity'] = query_params['ssl_verify_identity'][0] == 'true'
        
        # Connect to database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            **ssl_params
        )
        
        with connection.cursor() as cursor:
            # Check what's in the mem0 table for the user
            cursor.execute("SELECT id, document, meta FROM mem0 WHERE JSON_EXTRACT(meta, '$.user_id') = %s", (user_id,))
            results = cursor.fetchall()
            
            print(f"Found {len(results)} records for user '{user_id}':")
            for row in results:
                print(f"ID: {row[0]}")
                print(f"Document: {row[1]}")
                print(f"Meta: {row[2]}")
                print("---")
        
        connection.close()
        return results
        
    except Exception as e:
        print(f"Database check error: {e}")
        return []

def test_memory_persistence():
    """Test memory persistence issue"""
    user_id = "debug_user"
    
    print("=== Testing Memory Persistence Issue ===")
    
    # Clean up any existing data
    print("\n1. Cleaning up existing data...")
    memory_service.delete_memories(user_id)
    check_database_for_user(user_id)
    
    # Step 1: Add initial memory
    print("\n2. Adding initial memory...")
    result1 = memory_service.add_memory([
        {"role": "user", "content": "My name is Alice"},
        {"role": "assistant", "content": "Nice to meet you, Alice!"}
    ], user_id)
    print(f"Add result: {result1}")
    
    # Check database after first add
    print("\n3. Database state after adding name:")
    records_after_add = check_database_for_user(user_id)
    
    # Step 2: Search for memories
    print("\n4. Searching for memories...")
    memories = memory_service.search_memories("name", user_id)
    print(f"Search result: {memories}")
    
    # Step 3: Add a non-conflicting memory (this should NOT trigger deletion)
    print("\n5. Adding non-conflicting memory...")
    result2 = memory_service.add_memory([
        {"role": "user", "content": "I like coffee"},
        {"role": "assistant", "content": "That's great! Coffee is wonderful."}
    ], user_id)
    print(f"Add result: {result2}")
    
    # Check database after second add
    print("\n6. Database state after adding coffee preference:")
    records_after_second = check_database_for_user(user_id)
    
    # Step 4: Search for memories again
    print("\n7. Searching for memories again...")
    memories_after = memory_service.search_memories("name", user_id)
    print(f"Search result: {memories_after}")
    
    # Analysis
    print("\n=== ANALYSIS ===")
    print(f"Records after name: {len(records_after_add)}")
    print(f"Records after coffee: {len(records_after_second)}")
    
    if len(records_after_add) > 0 and len(records_after_second) == 0:
        print("❌ BUG CONFIRMED: Non-conflicting memory addition caused deletion of existing memories")
    elif len(records_after_add) > 0 and len(records_after_second) >= len(records_after_add):
        print("✅ WORKING CORRECTLY: Non-conflicting memory addition preserved existing memories")
    else:
        print("❓ UNCLEAR: Unexpected behavior detected")
    
    return len(records_after_add), len(records_after_second)

if __name__ == "__main__":
    test_memory_persistence()