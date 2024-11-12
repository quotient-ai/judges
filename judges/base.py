import json

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from openai import OpenAI

from judges.voting_methods import AVAILABLE_VOTING_METHODS

if TYPE_CHECKING:
    import pydantic


@dataclass
class Judgment:
    """
    A dataclass that represents a judgment.
    """

    score: bool | int
    reasoning: str


@dataclass
class Verdict:
    """
    A dataclass that represents a jury's verdict.
    """

    score: bool | int
    judgments: list[Judgment] = None


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
        user_prompt += (
            'Respond in JSON format. {{"REASONING": "[...]", "SCORE": "<your-score>"}}'
        )

        messages.append({"role": "user", "content": user_prompt})
        return messages

    def _judge(self, user_prompt: str, system_prompt: Optional[str] = None):
        messages = self._build_messages(user_prompt, system_prompt)
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
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
    ) -> Judgment:
        """
        Judge the input and return a verdict.
        """
        raise NotImplementedError("All judges must implement a judge method")


@dataclass
class Jury:
    """
    A jury is a set of judges that averages or takes the mode of all the scores.

    @misc{2404.18796,
        Author = {Pat Verga and Sebastian Hofstatter and Sophia Althammer and Yixuan Su and Aleksandra Piktus and Arkady Arkhangorodsky and Minjie Xu and Naomi White and Patrick Lewis},
        Title = {Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models},
        Year = {2024},
        Eprint = {arXiv:2404.18796},
    }
    """

    def __init__(self, judges: list[BaseJudge], voting_method: str = "majority"):
        self.judges = judges
        self.voting_method = AVAILABLE_VOTING_METHODS[voting_method]

    def vote(
        self,
        input: str,
        output: Optional[str] = None,
        expected: Optional[str] = None,
    ) -> Verdict:

        judgments = []
        for judge in self.judges:
            judgment = judge.judge(
                input=input,
                output=output,
                expected=expected,
            )

            judgments.append(judgment)

        scores = [judgment.score for judgment in judgments]
        score = self.voting_method(scores=scores)
        return Verdict(score=score, judgments=judgments)
