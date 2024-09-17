from unittest.mock import patch

from judges.base import Verdict

from judges.classifiers.correctness import CorrectnessJudge
from judges.graders.quality import QueryQualityJudge
from judges.graders.relevancy import RelevancyJudge


def mock_verdict(verdict: Verdict):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch("judges.base.openai.OpenAI.chat.completions.create") as mock:
                mock.return_value = verdict
                 # Pass the mock to the test
                return func(mock, *args, **kwargs)
        return wrapper
    return decorator


@mock_verdict(
    Verdict(
        score="average",
        reasoning="The query is moderately clear and specific. It may require some additional information for a complete understanding.",
    )
)
def test_quality_judge(mockclient):
    judge = QueryQualityJudge()
    verdict = judge.judge(input="What is the capital of France?")

    assert verdict.score == "average"
    assert (
        verdict.reasoning
        == "The query is moderately clear and specific. It may require some additional information for a complete understanding."
    )
    mockclient.assert_called_once()


@mock_verdict(
    Verdict(
        score="correct",
        reasoning="The answer correctly and fully answers the question.",
    )
)
def test_correctness_judge(mockclient):
    judge = CorrectnessJudge()
    verdict = judge.judge(
        input="What is the capital of France?",
        output="Paris",
        expected="Paris is the capital of France.",
    )

    assert verdict.score == "correct"
    assert verdict.reasoning == "The answer correctly and fully answers the question."

    mockclient.assert_called_once()


@mock_verdict(
    Verdict(
        score=2,
        reasoning="The question is highly relevant to the document.",
    )
)
def test_relevancy_judge(mockclient):
    judge = RelevancyJudge()
    verdict = judge.judge(
        input="What is the capital of France?",
        output="Paris is the capital of France.",
    )

    assert verdict.score == 2
    assert verdict.reasoning == "The question is highly relevant to the document."
    mockclient.assert_called_once()