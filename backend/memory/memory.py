from app.core.config import settings
from openai import OpenAI
from datetime import datetime
from prompts import SYSTEM_PROMPT, FACT_EXTRACTION_PROMPT, UPDATE_MEMORY_PROMPT
from llms import OpenAILLM
from embedding import OpenAIEmbeddingModel

class Memory:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.fact_update_memory_prompt = UPDATE_MEMORY_PROMPT

        self.embedder = OpenAIEmbeddingModel
        self.llm = OpenAILLM

        



