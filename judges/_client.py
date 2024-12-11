import logging

import openai

openai._utils._logs.logger.setLevel(logging.WARNING)
openai._utils._logs.httpx_logger.setLevel(logging.WARNING)

def llm_client(self):
    try:
        import litellm
    except ImportError:
        # fallback to openai
        client = openai.OpenAI()
        return client
    else:
        return litellm