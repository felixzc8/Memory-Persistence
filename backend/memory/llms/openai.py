from app.core.config import settings
from typing import List, Dict, Optional
from openai import OpenAI

class OpenAILLM:
    def __init__(self):
        self.model = settings.model_choice
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None, response_format: str = None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            response_format=response_format)
        
        return response.choices[0].message.content