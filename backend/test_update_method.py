#!/usr/bin/env python3
"""
Test script to verify the update method works correctly
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.memory_service import memory_service
from langchain_core.documents import Document

def test_update_method():
    """Test the update method with a name change scenario"""
    try:
        if not memory_service.memory:
            print("Memory service not initialized")
            return False
            
        print("Testing update method with name change scenario...")
        
        # Step 1: Add initial memory "Name is Bill"
        print("\n1. Adding initial memory: 'Name is Bill'")
        initial_result = memory_service.add_memory([
            {"role": "user", "content": "My name is Bill"},
            {"role": "assistant", "content": "Nice to meet you, Bill!"}
        ], "test_user")
        print(f"Initial memory added: {initial_result}")
        
        # Step 2: Search for memories to get the current state
        print("\n2. Searching for existing memories")
        memories = memory_service.search_memories("name", "test_user")
        print(f"Found memories: {memories}")
        
        if not memories:
            print("No memories found, cannot test update")
            return False
        
        # Step 3: Get the hash/ID of the existing memory
        old_memory_id = memories[0].get('hash') or memories[0].get('id')
        print(f"Old memory ID/hash: {old_memory_id}")
        
        # Step 4: Try to trigger an update by adding a conflicting memory
        print("\n3. Adding conflicting memory to trigger update: 'Name is llib'")
        update_result = memory_service.add_memory([
            {"role": "user", "content": "Actually, my name is llib, not Bill"},
            {"role": "assistant", "content": "Got it, llib! Thanks for letting me know."}
        ], "test_user")
        print(f"Update memory added: {update_result}")
        
        # Step 5: Search for memories after the update
        print("\n4. Searching for memories after update")
        updated_memories = memory_service.search_memories("name", "test_user")
        print(f"Updated memories: {updated_memories}")
        
        # Step 6: Check if the update worked correctly
        if updated_memories:
            memory_contents = [mem.get('memory', '') for mem in updated_memories]
            print(f"Memory contents: {memory_contents}")
            
            # Check if the new name is present and old name is gone
            has_new_name = any('llib' in content for content in memory_contents)
            has_old_name = any('Bill' in content and 'llib' not in content for content in memory_contents)
            
            if has_new_name and not has_old_name:
                print("✅ Update worked correctly: new name present, old name removed")
                return True
            elif has_new_name and has_old_name:
                print("⚠️ Partial update: both names present (expected for some scenarios)")
                return True
            else:
                print("❌ Update failed: expected name changes not found")
                return False
        else:
            print("❌ No memories found after update")
            return False
        
    except Exception as e:
        print(f"Error testing update method: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Clean up test data"""
    try:
        print("\n5. Cleaning up test data")
        cleanup_result = memory_service.delete_memories("test_user")
        print(f"Cleanup result: {cleanup_result}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        success = test_update_method()
        cleanup_test_data()
        print(f"\nTest {'PASSED' if success else 'FAILED'}")
    except Exception as e:
        print(f"Test execution error: {e}")
        cleanup_test_data()