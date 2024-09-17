from functools import partial
from textwrap import dedent
from typing import Optional

from judges.base import BaseJudge, Verdict

class CorrectnessJudge(BaseJudge):
    """
    Judge that determines if the output is correct.
    """
    citation = dedent(r"""
        @article{FILLMEIN,
            title={FILLMEIN},
            author={FILLMEIN},
            journal={FILLMEIN},
            year={FILLMEIN},
            volume={FILLMEIN},
            url={FILLMEIN}
        }
    """)
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
        system_prompt = None
        user_prompt = dedent(f"""
        You are given a QUESTION, an ANSWER and a REFERENCE. 
        You must determine whether the given ANSWER correctly answers the QUESTION based on the REFERENCE. 
                             
        Here is the data:
                             
        [BEGIN DATA]
        ************
        [Question]: {input}
        ************
        [Reference]: {expected}
        ************
        [Answer]: {output}
        [END DATA]

        Your response must be a single word, either "correct" or "incorrect",
        and should not contain any text or characters aside from that word.

        "correct" means that the question is correctly and fully answered by the answer.
        "incorrect" means that the question is not correctly or only partially answered by the
        answer.
        """)


correctness = partial(CorrectnessJudge)