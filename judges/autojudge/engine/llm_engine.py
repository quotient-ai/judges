from pydantic import BaseModel
import os
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import List, Literal
from openai import OpenAI
import instructor

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_API_KEY'] = openai_api_key


# Initialize the OpenAI client
openai_client = OpenAI(api_key=openai_api_key)
model = "gpt-4-turbo-2024-04-09"

class Recommendation(BaseModel):
    Reasoning: str
    Revision: str

class GradingNote(BaseModel):
    SCORE: bool
    REASONING: str

class LLMRequest(BaseModel):
    content: str
    model: str = "gpt-4-turbo-2024-04-09"
    response_model: Literal['Recommendation', 'GradingNote', None] = None
    system_prompt: str = None
    temperature: float = 0.3

class LLMRecommendationEngine:
    def __init__(self):
        self.openai_client = OpenAI()
        self.client = instructor.from_openai(openai_client)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def get_llm_completion(self, content, model="gpt-4-turbo-2024-04-09", response_model=None, system_prompt=None, temperature=0.3):
        messages = [{"role": "user", "content": content}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        response = self.client.chat.completions.create(
            model=model,
            response_model=response_model,
            max_tokens=1024,
            temperature=temperature,
            messages=messages, 
            seed=42
        )
        return response
