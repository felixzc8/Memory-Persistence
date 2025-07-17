from app.core.config import settings
from typing import List, Dict, Optional
from openai import OpenAI

class OpenAILLM:
    def __init__(self):
        self.model = settings.model_choice
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_response(self, instructions: str, input: List[Dict[str, str]], text_format: str = None):
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=input,
            text_format=text_format)
        
        return response.output_parsed