from typing import List, Dict, Optional
from openai import OpenAI
from pydantic import BaseModel
from ..config.base import MemoryConfig

class OpenAILLM:
    def __init__(self, config: MemoryConfig):
        self.model = config.model_choice
        self.client = OpenAI(api_key=config.openai_api_key)

    def generate_parsed_response(self, instructions: str, input: List, text_format: str = None):
        response = self.client.responses.parse(
            model=self.model,
            instructions=instructions,
            input=input,
            text_format=text_format)
        
        return response
    
    def generate_response(self, instructions: str, input):
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=input)
        
        return response
