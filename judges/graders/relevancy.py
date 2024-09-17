from functools import partial
from textwrap import dedent
from typing import Optional

from judges.base import BaseJudge, Verdict


class RelevancyJudge(BaseJudge):
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
        You are tasked with creating a system that can detect the relevance of a DOCUMENT to a QUESTION.

        Given a DOCUMENT and QUESTION you must provide a SCORE on an integer scale of 0 to 2 with the following meanings:

        0 = Represents that the QUESTION is irrelevant to the DOCUMENT
        1 = Represents that the QUESTION is somewhat relevant to the DOCUMENT
        2 = Represents that the QUESTION is highly relevant to the DOCUMENT

        Show your reasoning.

        ### Instruction
        Assign a relevancy score of 1 if the QUESTION is somewhat related to the DOCUMENT and CONTEXT, a score of 2 if QUESTION is highly relevant. 
        If none of the above satisfies give it a score of 0.

        ### Input
        QUESTION: {input}
        DOCUMENT: {output}

        Your output should be in JSON FORMAT with the keys "REASONING" and "SCORE":
        {{"REASONING": <your reasoning as bullet points>, "SCORE": <your final score>}}
        """
        )
        completion = self._get_completion(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )
        reasoning = completion.choices[0].message.content["reasoning"]
        score = completion.choices[0].message.content["score"]
        return Verdict(score=score, reasoning=reasoning)

relevancy = partial(RelevancyJudge)