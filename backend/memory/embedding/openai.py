from app.core.config import settings
from openai import OpenAI

class OpenAIEmbeddingModel:
    def __init__(self):
        self.model = settings.embedding_model
        self.model_dims = settings.embedding_model_dims

        api_key = settings.openai_api_key
        self.client = OpenAI(api_key=api_key)

    def embed(self, text: str):
        response = self.client.embeddings.create(
            input=text,
            model=self.model,
            dimensions=self.model_dims
        )
        return response.data[0].embedding