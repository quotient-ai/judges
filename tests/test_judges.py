from unittest.mock import patch

import openai

from judges.base import BaseJudge, Verdict
from judges.classifiers.correctness import CorrectnessJudge
from judges.graders.quality import QueryQualityJudge
from judges.graders.relevancy import RelevancyJudge


def mock_verdict(verdict: Verdict):
    def decorator(func):
        def wrapper(*args, **kwargs):
            openai.api_type = 'openai'
            with patch("openai.chat.completions.create") as mock:
                mock.return_value = verdict
                 # Pass the mock to the test
                return func(mock, *args, **kwargs)
        return wrapper
    return decorator


def test_base_judge_no_citation():


    try:
        class TestJudge(BaseJudge):
            pass
    except TypeError as e:
        assert str(e) == "can't instantiate abstract class TestJudge without citation attribute defined"

def test_base_judge():
    class TestJudge(BaseJudge):
        citation = "Test"

    judge = TestJudge("gpt-4o-mini")
    assert judge.model == "gpt-4o-mini"
    assert judge._client is not None


# @mock_verdict(
#     Verdict(
#         score="average",
#         reasoning="The query is moderately clear and specific. It may require some additional information for a complete understanding.",
#     )
# )
# def test_quality_judge(mockclient):
#     judge = QueryQualityJudge(model="gpt-4o-mini")
#     verdict = judge.judge(input="What is the capital of France?")

#     assert verdict.score == "average"
#     assert (
#         verdict.reasoning
#         == "The query is moderately clear and specific. It may require some additional information for a complete understanding."
#     )
#     mockclient.assert_called_once()


# @mock_verdict(
#     Verdict(
#         score="correct",
#         reasoning="The answer correctly and fully answers the question.",
#     )
# )
# def test_correctness_judge(mockclient):
#     judge = CorrectnessJudge(model="gpt-4o-mini")
#     verdict = judge.judge(
#         input="What is the capital of France?",
#         output="Paris",
#         expected="Paris is the capital of France.",
#     )

#     assert verdict.score == "correct"
#     assert verdict.reasoning == "The answer correctly and fully answers the question."

#     mockclient.assert_called_once()


# @mock_verdict(
#     Verdict(
#         score=2,
#         reasoning="The question is highly relevant to the document.",
#     )
# )
# def test_relevancy_judge(mockclient):
#     judge = RelevancyJudge(model="gpt-4o-mini")
#     verdict = judge.judge(
#         input="What is the capital of France?",
#         output="Paris is the capital of France.",
#     )

#     assert verdict.score == 2
#     assert verdict.reasoning == "The question is highly relevant to the document."
#     mockclient.assert_called_once()