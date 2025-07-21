from app.core.config import settings
from typing import List, Dict, Optional
from openai import OpenAI
from pydantic import BaseModel

class OpenAILLM:
    def __init__(self):
        self.model = settings.model_choice
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_response(self, instructions: str, input: List[Dict[str, str]], text_format: str = None):
        response = self.client.responses.parse(
            model=self.model,
            instructions=instructions,
            input=input,
            text_format=text_format)
        
        return response
