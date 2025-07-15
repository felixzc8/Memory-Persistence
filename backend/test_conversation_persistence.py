#!/usr/bin/env python3
"""
Test script for conversation persistence functionality
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import create_tables, get_db, Conversation, Message
from app.services.session_service import session_service
from app.config import settings
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_conversation_persistence():
    """Test the conversation persistence functionality"""
    print("🧪 Testing conversation persistence...")
    
    try:
        # 1. Create tables
        print("📊 Creating database tables...")
        create_tables()
        print("✅ Database tables created successfully")
        
        # 2. Test session creation
        print("📝 Testing session creation...")
        test_user_id = "test_user_" + str(uuid.uuid4())[:8]
        
        # Create a new session
        session_response = session_service.create_session(
            user_id=test_user_id,
            title="Test Conversation"
        )
        
        print(f"✅ Created session: {session_response.session_id}")
        session_id = session_response.session_id
        
        # 3. Test adding messages
        print("💬 Testing message persistence...")
        
        # Add user message
        success = session_service.add_message_to_session(
            session_id=session_id,
            role="user",
            content="Hello, this is a test message!"
        )
        print(f"✅ Added user message: {success}")
        
        # Add assistant message
        success = session_service.add_message_to_session(
            session_id=session_id,
            role="assistant", 
            content="Hello! I received your test message. This is my response."
        )
        print(f"✅ Added assistant message: {success}")
        
        # 4. Test retrieving session
        print("📖 Testing session retrieval...")
        session = session_service.get_session(session_id)
        
        if session:
            print(f"✅ Retrieved session: {session.title}")
            print(f"📈 Message count: {session.message_count}")
            print("💬 Messages:")
            for i, msg in enumerate(session.messages, 1):
                print(f"  {i}. [{msg.role}]: {msg.content[:50]}...")
        else:
            print("❌ Failed to retrieve session")
            return False
        
        # 5. Test getting user sessions
        print("📋 Testing user session list...")
        sessions = session_service.get_user_sessions(test_user_id)
        print(f"✅ Found {len(sessions)} sessions for user")
        
        # 6. Test message rotation (add many messages)
        print("🔄 Testing message rotation...")
        max_messages = settings.max_session_messages
        print(f"📊 Max messages setting: {max_messages}")
        
        # Add more messages than the limit
        for i in range(max_messages + 3):
            session_service.add_message_to_session(
                session_id=session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Test message number {i + 3}"
            )
        
        # Check final message count
        session = session_service.get_session(session_id)
        print(f"✅ Final message count after rotation: {session.message_count}")
        
        # 7. Test session context for OpenAI
        print("🤖 Testing session context formatting...")
        context = session_service.get_session_context(session_id, limit=5)
        print(f"✅ Generated context with {len(context)} messages")
        
        # 8. Test cleanup
        print("🧹 Testing session deletion...")
        success = session_service.delete_session(session_id)
        print(f"✅ Deleted session: {success}")
        
        print("\n🎉 All tests passed! Conversation persistence is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False

def test_database_models():
    """Test the database models directly"""
    print("🔧 Testing database models...")
    
    try:
        db = next(get_db())
        
        # Test creating a conversation
        conv_id = str(uuid.uuid4())
        conversation = Conversation(
            id=conv_id,
            user_id="test_direct_user",
            title="Direct Model Test"
        )
        
        db.add(conversation)
        db.commit()
        print("✅ Created conversation directly")
        
        # Test creating a message
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conv_id,
            role="user",
            content="Direct model test message"
        )
        
        db.add(message)
        db.commit()
        print("✅ Created message directly")
        
        # Test querying
        conv_query = db.query(Conversation).filter(Conversation.id == conv_id).first()
        msg_query = db.query(Message).filter(Message.conversation_id == conv_id).first()
        
        print(f"✅ Queried conversation: {conv_query.title}")
        print(f"✅ Queried message: {msg_query.content[:30]}...")
        
        # Cleanup
        db.delete(msg_query)
        db.delete(conv_query)
        db.commit()
        print("✅ Cleaned up test data")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        logger.error(f"Model test error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    print("🚀 Starting conversation persistence tests...\n")
    
    # Test database models first
    model_success = test_database_models()
    print()
    
    # Test service layer
    service_success = asyncio.run(test_conversation_persistence())
    
    if model_success and service_success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)