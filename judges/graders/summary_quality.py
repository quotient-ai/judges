from textwrap import dedent
from typing import Optional

from judges.base import BaseJudge, Judgment

HYPOEVAL_ASPECT_HYPOTHESIS_MAPPING = {
    "summary_coherence": [
        "A summary that effectively employs transitional phrases and cohesive devices to link sentences and ideas will likely receive a score of 4 or 5, as these elements enhance the flow and clarity of the narrative. Conversely, a summary that lacks these cohesive elements, resulting in abrupt transitions or a choppy narrative, will likely receive a score of 1 or 2. Summaries that use some transitions but still have noticeable gaps in cohesion or clarity, such as inconsistent use of linking words or phrases, may receive a score of 3.",
        "A summary that demonstrates good coherence, effectively connecting ideas and presenting information in a way that is easy to follow, will likely receive a score of four, despite minor issues (Key Finding: Score of 4).",
        "Summaries that are coherent and well-organized, effectively conveying the main ideas with clear transitions, will receive a score of 4. However, they may still have minor issues that prevent them from being fully polished.",
        "The engagement level of the summary, including its ability to maintain reader interest and convey a compelling narrative, influences coherence scores. Summaries that are engaging, articulate, and resonate with the reader will receive higher scores (4 or 5), while those that are dull, monotonous, or fail to capture the reader's attention will receive lower scores (1 or 2). A summary that captivates the audience and presents information in an interesting way will likely score a 5, while a lackluster summary will score a 1.",
        "Summaries that show a minimal level of coherence through a temporal relationship will receive a score of 3. They may suggest a connection but lack a strong inferential link, making them somewhat understandable but not fluid.",
    ],
    "summary_consistency": [
        "Summaries that contain significant factual inaccuracies or hallucinations, where the content does not align with the source document at all, will receive a score of 1. For instance, \"a summary that misrepresents the main ideas or includes irrelevant details\" would be deemed very poor.",
        "A summary that employs precise language and terminology consistent with the source text, enhancing clarity and understanding, will receive a score of 5. A summary that uses vague, incorrect, or misleading terminology that misrepresents the facts will receive a score of 1. A summary that uses mostly correct terminology but includes some inaccuracies or vague language will receive a score of 2 if the inaccuracies are substantial, or a score of 3 if they are minor.",
        "A summary that accurately represents the tone, style, and emotional elements of the original text, ensuring that the overall sentiment is preserved, will receive a score of 5. A summary that captures the tone but lacks some stylistic elements or nuances, while still conveying the intended sentiment, may receive a score of 4. A summary that conveys a different tone or style while retaining some factual accuracy but misrepresents the emotional context will likely receive a score of 3. A summary that misrepresents the tone or style significantly, leading to a different interpretation of the text, will receive a score of 2. A summary that fails to reflect the tone or style of the source text entirely, resulting in a loss of meaning, will receive a score of 1.",
        "Summaries that perfectly encapsulate the essence of the original passage, maintaining high coherence and clarity, will receive a score of 5. They should \"include all relevant information and present it in a well-structured manner,\" demonstrating a strong alignment with the original content.",
        "Summaries that are poorly organized, lack coherence, and fail to connect key ideas will receive a score of 1. They may \"contain irrelevant information or be overly simplistic,\" making it difficult for readers to understand the main points.",
    ],
    "summary_fluency": [
        "Summaries that are exceptionally well-written, characterized by clear, concise, and grammatically correct sentences will receive a score of 5. They present the information in a coherent and engaging manner, fully capturing the essence of the original passage while maintaining a natural flow of ideas.",
        "Summaries that consist of run-on sentences or overly complex sentence structures that significantly hinder readability and comprehension will receive a score of 1. Summaries that contain some run-on sentences but are generally understandable, albeit awkward, will receive a score of 2. Summaries that effectively use a mix of simple and compound sentences, though they may still have some awkward constructions that affect readability, will receive a score of 3. Summaries that predominantly use clear and concise sentences with minimal complexity and good readability will receive a score of 4. Summaries that utilize varied sentence structures effectively while maintaining clarity and enhancing engagement will receive a score of 5.",
        "A summary that includes vague references and minimal organization will likely receive a score of 2, as it leads to confusion about the main ideas (Key Findings: Score of 2).",
        "A summary that is well-structured, mostly free of grammatical errors, and effectively conveys the main ideas will receive a score of 4, as it demonstrates good coherence and flow (Key Findings: Score of 4).",
        "Summaries that consist of run-on sentences or overly complex sentence structures that severely hinder readability and comprehension will receive a score of 1. Summaries that have some run-on sentences or overly complex structures but still manage to communicate the main points, albeit with difficulty, will receive a score of 2. Summaries that effectively use a mix of simple and complex sentences, maintaining a reasonable level of readability but with some complexity, will receive a score of 3. Summaries that primarily use clear and concise sentences with minimal complexity, enhancing readability and understanding, will receive a score of 4. Summaries that utilize varied sentence structures effectively while maintaining clarity, conciseness, and engagement will receive a score of 5.",
    ],
    "summary_informativeness": [
        "Summaries that provide a basic understanding of the content but do not fully engage with the nuances will receive a score of 3, while summaries that capture all key points and nuances will receive a score of 5.",
        "The ability of a summary to accurately capture the main ideas and themes of the original text is crucial for its informativeness score. A score of 1 would be assigned to summaries that completely omit the main ideas, providing no insight into the text. A score of 2 would be given to summaries that mention some main ideas but do so in a vague or confusing manner, lacking clarity and context. A score of 3 would be for summaries that identify the main ideas but fail to provide depth or important supporting details, resulting in a basic understanding. A score of 4 would be assigned to summaries that clearly articulate the main ideas with relevant context and details, making them informative and engaging. Finally, a score of 5 would be given to summaries that comprehensively convey the main ideas, themes, and their significance in a coherent and engaging manner, enhancing the reader's understanding and connection to the text.",
        "Summaries that effectively synthesize the main ideas, provide context, and highlight implications of the source text while maintaining clarity and coherence will receive a score of 5, whereas summaries that merely restate the source text without any analysis, synthesis, or contextualization will receive a score of 2.",
        "A summary that includes direct quotes or specific examples from the source text to illustrate key points will be rated higher for informativeness, potentially receiving a score of 5. A summary that paraphrases key points without providing supporting evidence or examples, resulting in a lack of depth and specificity, will likely receive a lower score, such as 3 or 4, indicating that while it captures some key ideas, it does not fully engage with the source material or provide a comprehensive understanding.",
        "A summary that captures most key points from the source text but misses critical context or nuances, resulting in a less comprehensive understanding, will receive a score of 4, suggesting that it is informative but not fully complete. In contrast, a summary that comprehensively covers all major points, relevant examples, and context from the source text, while maintaining clarity and coherence, will receive a score of 5, indicating a high level of informativeness.",
    ],
    "summary_relevance": [
        "A summary that effectively captures all the main topics of the passage with clarity and coherence will receive a score of 5, as it provides a comprehensive understanding of the source material (Key Finding: \"A summary that effectively captures all the main topics of the passage with clarity and coherence...\").",
        "A summary that accurately reflects the factual information presented in the source text, including dates, statistics, and specific details, while maintaining clarity and coherence, will receive a score of 5. A summary that contains some accurate information but includes errors or omissions that could mislead the reader will receive a score of 4. A summary that presents a mix of accurate and inaccurate information, leading to confusion about the main ideas, will receive a score of 3. A summary that contains mostly incorrect information or significant inaccuracies that misrepresent the source text will receive a score of 2. A summary that is entirely factually incorrect or unrelated to the source text will receive a score of 1.",
        "Summaries that are concise yet comprehensive, covering all essential points of the source text without unnecessary elaboration or redundancy, will receive a score of 5. Summaries that are mostly concise but include some unnecessary details or minor redundancies will receive a score of 4. Summaries that are somewhat concise but miss key points or lack clarity will receive a score of 3. Summaries that are overly verbose, include irrelevant information, or fail to summarize the source text effectively will receive a score of 2. Summaries that are excessively long, poorly structured, and fail to convey the main ideas of the source text will receive a score of 1.",
        "Summaries that utilize precise and relevant terminology, demonstrating a thorough understanding of the subject matter and maintaining clarity throughout, will receive a score of 5. Summaries that predominantly use accurate language but contain some vague or imprecise terms that slightly hinder understanding will receive a score of 4. Summaries that mix accurate and inaccurate terminology, leading to confusion or misinterpretation, will receive a score of 3. Summaries that primarily use incorrect or misleading language, significantly affecting clarity, will receive a score of 2. Summaries that are filled with inaccuracies and misunderstandings, making them difficult to comprehend, will receive a score of 1.",
        "The degree to which a summary addresses the intended audience's needs and expectations will impact its relevance score. Summaries that are vague or fail to engage the audience will receive lower scores (1 or 2), while those that are informative, clear, and tailored to the audience's context will receive higher scores (4 or 5).",
    ],
}

HYPOEVAL_ASPECT_DEFINITION_MAPPING = {
    "summary_coherence": "Coherence measures the quality of all sentences collectively, focusing on how well they fit together and sound natural as a whole.",
    "summary_consistency": "Consistency measures whether the facts in the summary align with those in the original article, ensuring all facts are accurately reproduced and no untrue information is introduced.",
    "summary_fluency": "Fluency measures the quality of individual sentences, evaluating whether they are well-written and grammatically correct.",
    "summary_informativeness": "How well does the summary capture the key points of the article?",
    "summary_relevance": "Relevance measures how well the summary captures the key points of the article, considering whether all and only the important aspects are included.",
}

class HypoEvalSummaryQuality(BaseJudge):
    r"""
    A judge that evaluates from multiple aspects the quality of a summary of a given source text.
    For each aspect, it evaluates the summary on multiple decomposed dimensions (or hypotheses).
    The judge will not provide an overall score across all aspects, but provides a score for each aspect.

    Citation:
    ---------
    @misc{li2025hypoevalhypothesisguidedevaluationnatural,
        title={HypoEval: Hypothesis-Guided Evaluation for Natural Language Generation}, 
        author={Mingxuan Li and Hanchen Li and Chenhao Tan},
        year={2025},
        eprint={2504.07174},
        archivePrefix={arXiv},
        primaryClass={cs.CL},
        url={https://arxiv.org/abs/2504.07174}, 
    }

    Model(s) used in paper:
    -----------------------
    gpt-4o-mini, Llama-3.3-70B-Instruct
    """

    def judge(
        self,
        input: str,
        output: str,
        expected: Optional[str] = None,
    ):
        """
        Judge the quality of the summary of a source text from multiple aspects:
        coherence, consistency, fluency, informativeness, relevance

        Parameters:
        -----------
        input: str
            The query to generate summary, including the source text that is to be summarized.
        output: str
            The summary of the source text.
        expected: str
            The expected or ideal response (optional, can be used for reference or future enhancements).

        Returns:
        --------
        Judgment
            An object containing the grade and explanation.
            The grade is a string object containing scores on each aspect.
            The explanation also contains explanations on each decomposed dimension of each aspect.
        """

        aspects = ["coherence", "consistency", "fluency", "informativeness", "relevance"]
        overall_score = ""
        overall_reasoning = ""
        for aspect in aspects:
            aspect_overall_score = 0.0
            aspect_overall_reasoning = ""
            definition = HYPOEVAL_ASPECT_DEFINITION_MAPPING[f"summary_{aspect}"]
            system_prompt = dedent(f"""
                You are a helpful assistant in answering questions about a summary of a story.
                You will be given the story, the summary, and a pattern that talks about a specific trait to evaluate the ${aspect} of the summary.
                You should be generous and not too strict when evaluating.
                The definition of ${aspect} is given by: ${definition}.
                Story: [story]
                Summary: [summary]
                Pattern: [hypothesis]
                The pattern talks about a specific trait that is related to the summary's score on ${aspect}.
                You need to evaluate the summary based on the trait and the rubric that the pattern talks about. 
                You should give a score (ranging from 1 to 5) on that trait according to the rubric.
            """)
            hypothesis_bank = HYPOEVAL_ASPECT_HYPOTHESIS_MAPPING[f"summary_{aspect}"]
            for hypothesis in hypothesis_bank:
                user_prompt = dedent(f"""
                    Given story, summary, and pattern:
                    Story: {input}
                    Summary: {output}
                    Pattern: {hypothesis}
                    The pattern talks about a specific trait that is related to the summary's score on {aspect}.
                    The definition of {aspect} is given by: {definition}
                    You need to evaluate the summary based on the trait and the rubric that the pattern talks about. 
                    You should give a score (ranging from 1 to 5) on that trait according to the rubric.
                    Follow the steps and provide reasoning when giving your score.
                    Step 1: What is the trait that the pattern talks about?
                    Step 2: Based on the trait and the rubric provided in the pattern, how is the summary on the trait?
                    Step 3 (final answer): Based on the rubric and your evaluations in step 2, what should be the score of the summary on the trait?
                    You should be generous and not too strict when evaluating.
                    Answer:
                """)
                reasoning, score = self._judge(
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                )
                aspect_overall_score += float(score) / len(HYPOEVAL_ASPECT_HYPOTHESIS_MAPPING[f"summary_{aspect}"])
                aspect_overall_reasoning += f"----------Details for scoring for {aspect} aspect on the following decomposed dimension:\n{hypothesis}\nScore: {score}\nReasoning: {reasoning}\n"
            overall_score += f"Overall score on {aspect}: {round(aspect_overall_score, 1)}\n"
            overall_reasoning += f"==========Reasoning for aspect {aspect}:\n{aspect_overall_reasoning}\n"
        return Judgment(overall_score, overall_reasoning)