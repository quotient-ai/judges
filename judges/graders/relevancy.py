from textwrap import dedent
from typing import Optional

from judges.base import BaseJudge, Verdict


class DocumentRelevancy(BaseJudge):
    r"""
    A judge that evaluates the relevancy of a document to a question.

    Citation:
    ---------
    @misc{
        vespa2024llmjudge,
        author       = {Jo Kristian Bergum},
        title        = {Improving Retrieval with LLM as a Judge},
        howpublished = {\url{https://blog.vespa.ai/improving-retrieval-with-llm-as-a-judge/}},
        note         = {Accessed: 2024-09-17},
        year         = {2024}
    }
    """
    def judge(
        self,
        input: str,
        output: Optional[str] = None,
        expected: Optional[str] = None,
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
        """
        )
        reasoning, score = self._judge(user_prompt=user_prompt, system_prompt=system_prompt)
        return Verdict(reasoning=reasoning, score=score)