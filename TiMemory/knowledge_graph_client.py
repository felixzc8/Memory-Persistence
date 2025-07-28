import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from .config.timemory_config import TiMemoryConfig

logger = logging.getLogger(__name__)

class KnowledgeGraphClient:
    def __init__(self, config: TiMemoryConfig):
        self.config = config
        self.base_url = config.knowledge_graph_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def save_personal_memory(
        self,
        chat_history: List[Dict[str, str]], 
        user_id: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Save chat history as personal memory to knowledge graph.
        
        Args:
            chat_history: List of message dictionaries with 'role' and 'content'
            user_id: User identifier
            session_id: Session identifier
        
        Returns:
            API response data or None if failed
        """
        url = f"{self.base_url}/api/v1/ingest/save"
        
        payload = {
            "input": chat_history,
            "metadata": {
                "user_id": user_id,
                "session_id": session_id
            },
            "target_type": "personal_memory",
            "input_type": "chat_history"
        }
        
        try:
            logger.info(f"Sending personal memory to knowledge graph for user {user_id}, session {session_id}")
            response = await self.client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully saved personal memory to knowledge graph: {result}")
                return result
            else:
                logger.error(f"Knowledge graph API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to call knowledge graph API: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()