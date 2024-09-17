from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
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


class BaseJudge:
    """
    Base class for all judges. All judges must implement a judge method which
    produces a `Verdict` object that contains a score and reasoning.

    The score is a boolean value, True if judge's criteria is met, False
    if not.

    The reasoning is a string that explains why the score is True or False.
    """
    citation: str = None

    def __init__(
        self,
        model: str,
    ):
        """
        Initialize the judge with a specific model.
        """
        self.model = model
        self._client = self._configure_client()

    def __init_subclass__(cls, **kwargs):
        for required in ("citation",):
            if not getattr(cls, required):
                raise TypeError(f"can't instantiate abstract class {cls.__name__} without {required} attribute defined")
        return super().__init_subclass__(**kwargs)

    def _configure_client(self):
        if self.model == "gpt-4o-mini":
            client = OpenAI()
        elif self.model == "gpt-4o":
            client = OpenAI()
        else:
            raise ValueError(f"Invalid model: {self.model}")

        return client
    
    def _get_completion(self, user_prompt: str, system_prompt: Optional[str] = None):
        messages = []
        if system_prompt is not None:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_prompt})

        completion = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        return completion

    def judge(
        self,
        input: str,
        output: str = None,
        expected: str = None,
        format: Optional["pydantic.BaseModel"] = None,
    ) -> Verdict:
        """
        Judge the input and return a verdict.
        """
        raise NotImplementedError("All judges must implement a judge method")
