from openai import OpenAI
from ..config.base import MemoryConfig

class OpenAIEmbeddingModel:
    def __init__(self, config: MemoryConfig):
        self.model = config.embedding_model
        self.model_dims = config.embedding_model_dims

        api_key = config.openai_api_key
        self.client = OpenAI(api_key=api_key)

    def embed(self, text: str):
        response = self.client.embeddings.create(
            input=text,
            model=self.model,
            dimensions=self.model_dims
        )
        return response.data[0].embedding