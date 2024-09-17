import json

from functools import partial
from textwrap import dedent
from typing import Optional

from judges.base import BaseJudge, Verdict

class QueryQualityJudge(BaseJudge):
    citation = dedent(r"""
        @article{xu2024magpie,
            title={Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing},
            author={Zhangchen Xu and Fengqing Jiang and Luyao Niu and Yuntian Deng and Radha Poovendran and Yejin Choi and Bill Yuchen Lin},
            journal={ArXiv},
            year={2024},
            volume={abs/2406.08464},
            url={https://api.semanticscholar.org/CorpusID:270391432}
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
        # Instruction
        You need to rate the quality of the QUERY based on its clarity, specificity, and coherence.

        The rating scale is as follows:

        − very poor: The QUERY is unclear, vague, or incoherent. It lacks essential information and
        context.
        − poor: The QUERY is somewhat unclear or lacks important details. It requires significant
        clarification.
        − average: The QUERY is moderately clear and specific. It may require some additional
        information for a complete understanding.
        − good: The QUERY is clear, specific, and mostly well−formed. It provides sufficient context for
        understanding the user’s intent.
        − excellent: The QUERY is very clear, specific, and well−articulated. It contains all the
        necessary information and context for providing a comprehensive response.

        ## Input
        QUERY: {input}

        ## Output Format
        Given the user QUERY, you first need to give an assessment, highlighting the strengths and/or
        weaknesses of the user QUERY. Then, you need to output a rating from very poor to
        excellent by filling in the placeholders in [...]. Respond in JSON format.

        {{"REASONING": "[...]", "SCORE": "[very poor/poor/average/good/excellent]"}}
        """
        )
        completion = self._get_completion(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )
        data = json.loads(completion.choices[0].message.content)
        reasoning = data["REASONING"]
        score = data["SCORE"]
        return Verdict(score=score, reasoning=reasoning)
    

query_quality = partial(QueryQualityJudge)