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

    score: bool | int | str
    reasoning: str

    def __post_init__(self):
        if self.score.lower() in ["yes", "true", 1, "good"]:
            self.score = True
        elif self.score.lower() in ["no", "false", 0, "bad"]:
            self.score = False


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
            "gpt-4": OpenAI(),
        }
        try:
            return model_map[self.model]
        except KeyError:
            raise ValueError(f"unsupported model: {self.model}")

    def _build_messages(self, user_prompt: str, system_prompt: Optional[str] = None):
        """
        Build a list of messages to be sent to the model, incorporating optional system-level instructions.

        Parameters:
        -----------
        user_prompt : str
            The main user prompt to be sent to the model.
        system_prompt : Optional[str], default=None
            An optional system-level prompt to provide additional context or guidelines.

        Returns:
        --------
        list
            A list of dictionaries, each representing a message to be sent to the model.
            The user prompt includes instructions to respond in JSON format.

        Notes:
        ------
        - The JSON format expectation is flexible, allowing for any fields to be included in the response.
        - This ensures compatibility with dynamically structured outputs.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add a flexible JSON format expectation to the user prompt
        user_prompt += (
            " Respond in JSON format with any relevant fields and values."
            " Ensure the output is valid JSON that can be parsed directly by Python's json module."
        )

        messages.append({"role": "user", "content": user_prompt})
        return messages

    def _judge(self, user_prompt: str, system_prompt: Optional[str] = None):
        """
        Send a prompt to the model and dynamically parse the JSON response.

        Parameters:
        -----------
        user_prompt : str
            The main user prompt to be sent to the model.
        system_prompt : Optional[str], default=None
            An optional system-level prompt to provide additional instructions or context.

        Returns:
        --------
        dict
            A dictionary containing all the fields extracted from the model's JSON response.

        Raises:
        -------
        ValueError
            If the response from the model cannot be parsed as valid JSON.

        Notes:
        ------
        - The method expects the model's response to be in JSON format.
        - Dynamically extracts all fields from the response, allowing flexible handling
          of various output structures without causing key errors.
        - Designed to handle scenarios where certain fields may be missing in the model's output.
        """
        messages = self._build_messages(user_prompt, system_prompt)
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
        )

        # Dynamically parse the JSON response
        try:
            data = json.loads(completion.choices[0].message.content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}")

        # Extract all available fields
        extracted_data = {key: data.get(key, None) for key in data}

        return extracted_data

    @abstractmethod
    def judge(
        self,
        input: str,
        output: Optional[str] = None,
        expected: Optional[str] = None,
    ) -> Judgment:
        """
        Judge the input and return a Judgment.

        Parameters:
        -----------
        input: str
            The input provided to the model to be judged.
        output: str
            The output generated by the model.
        expected: str
            The output that the model was expected to generate.
        """
        raise NotImplementedError("all judges must implement a judge method")


@dataclass
class Jury:
    r"""
    A jury is a set of judges that averages or takes the mode of all the scores.

    @misc{verga2024replacingjudgesjuriesevaluating,
        title={Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models},
        author={Pat Verga and Sebastian Hofstatter and Sophia Althammer and Yixuan Su and Aleksandra Piktus and Arkady Arkhangorodsky and Minjie Xu and Naomi White and Patrick Lewis},
        year={2024},
        eprint={2404.18796},
        archivePrefix={arXiv},
        primaryClass={cs.CL},
        url={https://arxiv.org/abs/2404.18796},
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
