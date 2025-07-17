from app.core.config import settings
from openai import OpenAI

class OpenAILLM:
    def __init__(self):
        self.model = settings.model_choice
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_response(self, messages: list[dict]):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages)