import logging

import instructor
import openai

from pydantic import BaseModel
from tenacity import retry, wait_random_exponential, stop_after_attempt

openai._utils._logs.logger.setLevel(logging.WARNING)
openai._utils._logs.httpx_logger.setLevel(logging.WARNING)


def llm_client():
    try:
        import litellm
    except ImportError:
        # fallback to openai
        client = openai.OpenAI()
        return client
    else:
        return litellm


@retry(
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(5),
)
def get_completion(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    seed: int,
    response_model: BaseModel = None,
):
    client = llm_client()

    if client.__class__.__name__ == "OpenAI":
        # TODO: autojudge uses the instructor client, but the rest of the judges do not.
        # FIX THIS.
        client = instructor.from_openai(client)
    elif hasattr(client, "__name__") and client.__name__ == "litellm":
        client = instructor.from_litellm(client.completion)
    else:
        raise Exception("unknown client. please create an issue on GitHub if you see this message.")
    
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=messages,
        seed=seed,
        response_model=response_model,
    )

    return response
