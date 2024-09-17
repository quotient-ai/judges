from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import json
from typing import TYPE_CHECKING, Optional

from openai import OpenAI

if TYPE_CHECKING:
    import pydantic


@dataclass
class Verdict:
    """
    A dataclass that represents a judge's verdict.
    """
    score: bool | int
    reasoning: str

@dataclass
class BaseJudge:
    """
    Base class for all judges. All judges must implement a judge method which
    produces a `Verdict` object that contains a score and reasoning.

    The score is a boolean value, True if judge's criteria is met, False
    if not.

    The reasoning is a string that explains why the score is True or False.
    """
    def __init__(
        self,
        model: str,
    ):
        """
        Initialize the judge with a specific model.
        """
        self.model = model
        self._client = self._configure_client()

    def _configure_client(self):
        model_map = {
            "gpt-4o-mini": OpenAI(),
            "gpt-4o": OpenAI(),
        }
        try:
            return model_map[self.model]
        except KeyError:
            raise ValueError(f"unsupported model: {self.model}")
    
    def _build_messages(self, user_prompt: str, system_prompt: Optional[str] = None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # add json format expectation to the user prompt:
        user_prompt += 'Respond in JSON format. {{"REASONING": "[...]", "SCORE": "<your-score>"}}'

        messages.append({"role": "user", "content": user_prompt})
        return messages

    def _judge(self, user_prompt: str, system_prompt: Optional[str] = None):
        messages = self._build_messages(user_prompt, system_prompt)
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        reasoning = data["REASONING"]
        score = data["SCORE"]
        return reasoning, score

    @abstractmethod
    def judge(
        self,
        input: str,
        output: Optional[str] = None,
        expected: Optional[str] = None,
        format: Optional["pydantic.BaseModel"] = None,
    ) -> Verdict:
        """
        Judge the input and return a verdict.
        """
        raise NotImplementedError("All judges must implement a judge method")
