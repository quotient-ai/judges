import os
from unittest.mock import patch

import openai
import openai_responses

from judges.base import Judgment
from judges.classifiers.correctness import PollMultihopCorrectness

os.environ['OPENAI_API_KEY'] = 'test-key'

def mock_judgment(judgment: Judgment):
    def decorator(func):
        def wrapper(*args, **kwargs):
            openai.api_type = 'openai'
            with patch("openai.chat.completions.create") as mock:
                mock.return_value = judgment
                 # Pass the mock to the test
                return func(mock, *args, **kwargs)
        return wrapper
    return decorator


@openai_responses.mock()
@mock_judgment(
    Judgment(
        score="average",
        reasoning="The query is moderately clear and specific. It may require some additional information for a complete understanding.",
    )
)
def test_quality_judge(mockclient):
    judge = PollMultihopCorrectness(model="gpt-4")
    judgment = judge.judge(input="What is the capital of France?")

    assert judgment.score == "average"
    assert (
        judgment.reasoning
        == "The query is moderately clear and specific. It may require some additional information for a complete understanding."
    )
    mockclient.assert_called_once()
