from textwrap import dedent

from judges.base import BaseJudge, Judgment

class AnswerCorrectness(BaseJudge):
    r"""
    A judge that evaluates the correctness of an answer to a question based on a reference.

    Citation:
    ---------
    None
    """
    def judge(
        self,
        input: str,
        output: str = None,
        expected: str = None,
    ) -> Judgment:
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

        Your response must be a single word, either True or False.
        and should not contain any text or characters aside from that word.

        True means that the question is correctly and fully answered by the answer.
        False means that the question is not correctly or only partially answered by the answer.
        """)
        reasoning, score = self._judge(user_prompt=user_prompt, system_prompt=system_prompt)
        return Judgment(reasoning=reasoning, score=score)

