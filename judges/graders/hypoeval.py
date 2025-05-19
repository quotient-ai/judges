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
    "story_coherence": [
        "A story that lacks meaningful connections between sentences or paragraphs will likely receive a score of 1, as it is poorly organized and difficult for readers to follow (Key Finding: \"A story receiving a score of one is likely to be poorly organized, lacking a clear structure or logical flow\").",
        "Stories that present a well-developed narrative with clear, logical connections between ideas will receive a score of 5, as they effectively communicate their message and engage the reader (Key Finding: \"A score of five is reserved for stories that exhibit excellent coherence...making it easy for readers to follow and understand\").",
        "A score of 1 is typically given to stories that feature abrupt and confusing transitions between scenes or ideas, resulting in a disjointed reading experience that leaves readers puzzled about the relationships between events. These transitions may lack logical connections or context, making it difficult to follow the narrative. Conversely, stories that achieve a score of 5 demonstrate smooth and logical transitions that guide the reader seamlessly from one idea to the next, enhancing clarity and maintaining engagement throughout the story.",
        "Stories rated with a score of 1 frequently include vague or abstract descriptions that fail to create a vivid sense of place or character, leading to a lack of immersion for the reader. These descriptions may be overly simplistic or generic, failing to engage the reader's imagination. In contrast, stories that receive a score of 5 are rich in detail, providing vivid and specific descriptions that effectively establish the setting and characters, drawing readers into the narrative and enhancing their overall experience, which contributes to a stronger sense of coherence.",
        "A story that flows logically with clear connections between events and effective use of transitions will likely receive a score of 4, as it engages the reader and evokes a strong sense of place and character (Key Finding: \"A score of four suggests a well-structured story that is coherent and engaging\").",
    ],
    "story_complexity": [
        "Stories that are simplistic and lack detail are likely to receive a score of one, while those that show some development of ideas may score two, and narratives that include rich descriptions and varied vocabulary may score four or five.",
        "A story that lacks depth and critical engagement with the prompt is likely to receive a score of one, while a narrative that shows some basic understanding of the prompt may score two, and those that demonstrate advanced critical thinking and nuanced arguments may score five.",
        "Stories that receive a score of 1 often feature a single, straightforward plotline with minimal character development, where characters are flat and do not face significant challenges. In contrast, stories that score a 5 are characterized by multiple intertwining plotlines, rich character arcs, and significant character growth, engaging the reader emotionally and intellectually through complex interpersonal dynamics.",
        "Stories that do not address the prompt meaningfully and consist of basic sentences are likely to receive a score of one, while those that show some attempt to engage with the prompt may score two, and narratives that fully address the prompt with depth and insight may score five.",
        "Stories that achieve a score of 5 are characterized by high complexity and creativity, featuring rich character development, intricate plots, and sophisticated use of language and literary devices. These narratives often surprise the reader with unique perspectives and profound themes, demonstrating a mastery of storytelling techniques.",
    ],
    "story_empathy": [
        "Stories that achieve a score of five are characterized by their exceptional ability to evoke empathy, featuring rich character development and a compelling narrative that fully engages the audience's empathy, as noted in the findings that \"these stories resonate deeply with readers.\"",
        "A score of one may also be associated with stories that present characters in a one-dimensional manner, showing little understanding of human emotions or experiences, as indicated by \"it may contain clichés or stereotypes, showing little understanding of human emotions or experiences.\"",
        "Stories that include vivid, specific, and sensory descriptions of characters' emotional states and their reactions to various circumstances will score higher on empathy (4 or 5). These narratives will paint a detailed picture of the characters' feelings, using rich imagery to evoke emotional responses in the reader. Conversely, stories that are abstract, lack detail, or fail to illustrate emotional responses will likely score lower (1 or 2), as they do not create a strong emotional connection with the reader. For instance, a story that describes a character's heart racing and palms sweating during a moment of fear will resonate more than one that simply states the character is scared without elaboration.",
        "Stories that achieve a score of 4 exhibit strong empathetic connections, showcasing well-developed characters with clear emotional arcs and relatable challenges. These narratives effectively engage the reader's emotions through thoughtful exploration of feelings and experiences, allowing for a deeper understanding of the characters.",
        "A score of 5 is reserved for stories that excel in emotional depth and character development, featuring complex characters and intricate plots that evoke strong emotional responses. These narratives resonate deeply with readers, fostering a profound empathetic connection and prompting significant reflection on the characters' experiences and feelings.",
    ],
    "story_engagement": [
        "Stories that lack coherence and clarity, with numerous grammatical errors and fail to engage the reader, will receive a score of 1, while stories that are well-structured, engaging, and evoke emotional responses will receive a score of 5.",
        "The originality and creativity of the story's premise and execution are crucial for engagement. A score of 1 is given to stories that are entirely derivative, relying on clichés and predictable plots without any unique elements. A score of 2 may indicate a story that includes a few original ideas but is largely uninspired and fails to captivate the reader. A score of 3 suggests a moderately creative premise that engages the reader but lacks depth or surprising twists. A score of 4 reflects a highly original story that captivates the audience with innovative concepts and engaging execution, while a score of 5 is reserved for stories that present unique, unexpected twists and thought-provoking insights that challenge the reader's expectations and provoke deeper reflection.",
        "Stories that are overly simplistic and fail to follow the prompt effectively will receive a score of 1, while those that showcase original ideas and a compelling narrative voice will receive a score of 5.",
        "A story that shows minimal engagement with the prompt and lacks interesting ideas will likely receive a score of 2, while a story that fully addresses the prompt with a compelling narrative will likely receive a score of 5.",
        "A story that is poorly structured and lacks clarity will receive a score of 1, while a story that is well-organized and engaging will receive a score of 4.",
    ],
    "story_grammaticality": [
        "A score of 2 indicates that while the story has some basic structure, it still suffers from significant grammatical issues and lacks clarity, as indicated by the observation that \"the narrative may show some attempt at creativity but is marred by awkward phrasing and frequent errors that hinder understanding.\"",
        "A score of 5 is indicative of stories that are free from errors and exhibit a high level of fluency, making them engaging and interesting, as noted in the finding that \"stories that achieve a score of five are exemplary in terms of grammatical accuracy and overall quality.\"",
        "A score of 2 may be given to stories that show minimal character development and a weak plot, leading to a lack of engagement, as noted in the finding that \"the narrative may show minimal character development and a weak plot.\"",
        "The presence of severe grammatical errors, such as incorrect verb tenses, subject-verb agreement issues, and frequent sentence fragments, will significantly lower the grammaticality score. Stories that exhibit a lack of basic grammatical understanding, resulting in incoherence and confusion, will receive a score of 1.0. Stories that contain numerous basic grammatical errors but still convey a somewhat coherent narrative will receive a score of 2.0. A score of 3.0 will indicate stories that contain some grammatical errors but maintain overall clarity and coherence, with occasional awkward phrasing. Stories that are well-structured with minimal errors, demonstrating a strong command of grammar and clarity, will receive a score of 4.0, while those that are nearly flawless in grammatical accuracy and sophistication, showcasing a high level of grammatical proficiency, will achieve a score of 5.0.",
        "The effective use of punctuation, including correct placement of commas, quotation marks, and avoidance of run-on sentences, will positively influence the grammaticality score. Stories with numerous punctuation errors that disrupt readability and comprehension will receive a score of 1.0, indicating severe issues in clarity. A score of 2.0 will reflect stories with frequent punctuation errors that hinder understanding and flow, while a score of 3.0 will show some errors but overall effective punctuation use that does not significantly detract from the narrative. Stories that utilize punctuation correctly to enhance clarity and meaning, with only minor errors that do not impede understanding, will receive a score of 4.0, while those that are flawless in punctuation and enhance the narrative through effective punctuation will achieve a score of 5.0, showcasing a high level of grammatical sophistication.",
    ],
    "story_likability": [
        "**Coherence and Structure**: Stories that exhibit a clear and coherent structure are more likely to receive higher likability scores. A score of one would be given to stories that are chaotic and poorly organized, while a score of five would be awarded to stories that are well-structured, with a logical flow and clear narrative progression.",
        "Stories that are somewhat coherent but still contain significant flaws, such as minor repetitive elements or a lack of logical flow, will receive a score of two (Key Findings: UNION: An Unreferenced Metric for Evaluating Open-ended Story Generation).",
        "A score of one will be assigned to stories that are poorly organized and fail to address the prompt adequately, containing irrelevant content and grammatical errors (Key Findings: Towards Evaluating Narrative Quality In Student Writing).",
        "A score of four will be given to well-written stories that demonstrate strong character development and evoke emotional responses, as these narratives are engaging and show a good understanding of the prompt (Key Findings: Investigating Rater/Prompt Interactions in Writing Assessment).",
        "Well-developed stories that engage the reader and provide vivid descriptions will likely receive a score of four, as they employ a variety of narrative techniques (Key Findings: Towards Evaluating Narrative Quality In Student Writing).",
    ],
    "story_relevance": [
        "Stories that receive a score of 1 may exhibit \"numerous grammatical errors\" and demonstrate a lack of understanding of writing conventions, making them difficult to comprehend.",
        "The clarity and coherence of the narrative structure play a critical role in determining the relevance score. A well-structured story that logically follows the prompt, maintains a clear focus, and presents ideas in a coherent manner will receive a score of 5.0. A story that has some logical flow but includes noticeable inconsistencies or distractions will score a 3.0. In contrast, a disjointed or confusing narrative that strays from the prompt or lacks logical progression will score a 1.0, indicating poor relevance.",
        "A score of 2 indicates that the story shows minimal relevance to the prompt, presenting vague ideas or poorly developed narratives that fail to engage the reader. These stories may include some relevant content but lack clarity, depth, or a satisfying conclusion. In contrast, stories rated with a score of 4 effectively engage with the prompt, presenting a coherent narrative that aligns closely with its requirements while incorporating unique perspectives or twists that enhance the story, demonstrating strong character development and maintaining reader interest.",
        "Stories that receive a score of 1 are likely to be incoherent and lack any meaningful engagement with the prompt, exhibiting \"poorly constructed\" narratives that fail to convey a clear message or emotional depth.",
        "Stories that receive a score of one are likely to be incoherent and chaotic, containing severe logical inconsistencies and failing to address the prompt effectively, as noted in the findings that \"stories that receive a score of one are likely to be incoherent and chaotic\" (Key Findings: OpenMEVA).",
    ],
    "story_surprise": [
        "The effectiveness of the story's thematic depth and its ability to challenge reader expectations plays a crucial role in determining surprise scores. Stories that present superficial themes or fail to engage with deeper moral or philosophical questions will likely score a 1, as they lack substance and insight. A score of 2 may be assigned to stories that touch on familiar themes but do not provide any significant insights or surprises, resulting in limited engagement. Stories that explore moderate themes with some unexpected revelations will score a 3, as they provide some depth but do not fully challenge the reader's understanding. A score of 4 is for narratives that delve into profound themes and lead to surprising insights that provoke thought and reflection, enhancing the overall experience. Finally, a score of 5 will be given to those that challenge the reader's understanding in unexpected ways, offering deep thematic explorations that resonate emotionally and intellectually, leaving a lasting impression.",
        "Stories that achieve a score of 5 on surprise are characterized by high levels of originality and creativity, containing unexpected elements that are \"not only surprising but also enhance the overall narrative experience,\" leading to a profound impact on the reader.",
        "The complexity and intricacy of the plot contribute significantly to the surprise score. Simple, linear narratives that lead to an expected conclusion will score a 1, while stories that introduce minor twists but remain largely predictable will score a 2. A score of 3 will be awarded to stories that contain moderate complexity with some unexpected developments, but these twists may not fully capitalize on the potential for surprise. Stories with multiple layers, red herrings, or intricate plots that culminate in a surprising twist will score a 4, while those that masterfully weave complexity into a surprising ending, challenging the reader's expectations throughout the narrative and providing a satisfying resolution, will receive a score of 5.",
        "The use of narrative devices such as foreshadowing, misdirection, and symbolism is crucial in determining the surprise score. Stories that lack any narrative devices and lead to a straightforward ending will receive a score of 1, as they fail to engage the reader's curiosity. Those that include minimal use of these devices but still result in predictable outcomes will score a 2, indicating a lack of effective storytelling techniques. A score of 3 will be given to stories that utilize some narrative devices effectively but lead to a moderately surprising conclusion that lacks depth. A score of 4 will be awarded to stories that skillfully employ multiple narrative devices to create a significant twist that enhances the narrative and engages the reader. Finally, a score of 5 will be for stories that expertly integrate a variety of narrative devices to deliver a shocking and unexpected ending that redefines the reader's understanding of the plot, showcasing a high level of narrative skill and creativity.",
        "A story that receives a score of 1 is likely to be \"predictable\" and \"lack originality,\" adhering closely to common themes or clichés without engaging the reader's curiosity or imagination.",
    ],
}

HYPOEVAL_ASPECT_DEFINITION_MAPPING = {
    "summary_coherence": "Coherence measures the quality of all sentences collectively, focusing on how well they fit together and sound natural as a whole.",
    "summary_consistency": "Consistency measures whether the facts in the summary align with those in the original article, ensuring all facts are accurately reproduced and no untrue information is introduced.",
    "summary_fluency": "Fluency measures the quality of individual sentences, evaluating whether they are well-written and grammatically correct.",
    "summary_informativeness": "How well does the summary capture the key points of the article?",
    "summary_relevance": "Relevance measures how well the summary captures the key points of the article, considering whether all and only the important aspects are included.",
    "story_coherence": "Coherence measures whether the story makes sense",
    "story_complexity": "Complexity measures how elaborate the story is",
    "story_empathy": "Empathy measures how well you understood the characters' emotions (regardless of whether you agreed with them)",
    "story_engagement": "Engagement measures how much you engaged with the story",
    "story_grammaticality": "How grammatically correct is the text of the story fragment?",
    "story_likability": "How enjoyable do you find the story fragment?",
    "story_relevance": "Relevance measures how well the story matches its prompt",
    "story_surprise": "Surprise measures how surprising the end of the story was",
}

class HypoEvalSummary(BaseJudge):
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
        

class HypoEvalStory(BaseJudge):
    r"""
    A judge that evaluates from multiple aspects the quality of a story in response to a given prompt.
    For each aspect, it evaluates the story on multiple decomposed dimensions (or hypotheses).
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
        Judge the quality of the generated story in response to a prompt from multiple aspects:
        coherence, complexity, empathy, engagement, grammaticality, likability, relevance, surprise

        Parameters:
        -----------
        input: str
            The query to generate story, containing the prompt.
        output: str
            The generated story in response to the prompt.
        expected: str
            The expected or ideal response (optional, can be used for reference or future enhancements).

        Returns:
        --------
        Judgment
            An object containing the grade and explanation.
            The grade is a string object containing scores on each aspect.
            The explanation also contains explanations on each decomposed dimension of each aspect.
        """

        aspects = ["coherence", "complexity", "empathy", "engagement", "grammaticality", "likability", "relevance", "surprise"]
        overall_score = ""
        overall_reasoning = ""
        for aspect in aspects:
            aspect_overall_score = 0.0
            aspect_overall_reasoning = ""
            definition = HYPOEVAL_ASPECT_DEFINITION_MAPPING[f"story_{aspect}"]
            system_prompt = dedent(f"""
                You are a helpful assistant in answering questions about a written story of a given prompt.
                You will be given the prompt, the written story, and a pattern that talks about a specific trait to evaluate the {aspect} of the story.
                You should be generous and not too strict when evaluating.
                The definition of {aspect} is given by: {definition}.
                Prompt: [prompt]
                Story: [story]
                Pattern: [hypothesis]
                The pattern talks about a specific trait that is related to the story's score on {aspect}.
                You need to evaluate the story based on the trait and the rubric that the pattern talks about. 
                You should give a score (ranging from 1 to 5) on that trait according to the rubric.
            """)
            hypothesis_bank = HYPOEVAL_ASPECT_HYPOTHESIS_MAPPING[f"story_{aspect}"]
            for hypothesis in hypothesis_bank:
                user_prompt = dedent(f"""
                    Given prompt, story, and pattern:
                    Prompt: {input}
                    Story: {output}
                    Pattern: {hypothesis}
                    Note: the story may have been abruptly cut in the middle of a sentence. Please rate it as if they ended just before the unfinished sentence.
                    The pattern talks about a specific trait that is related to the story's score on {aspect}.
                    The definition of {aspect} is given by: {definition}
                    You need to evaluate the story based on the trait and the rubric that the pattern talks about. 
                    You should give a score (ranging from 1 to 5) on that trait according to the rubric.
                    Follow the steps and provide reasoning when giving your score.
                    Step 1: What is the trait that the pattern talks about?
                    Step 2: Based on the trait and the rubric provided in the pattern, how is the story on the trait?
                    Step 3 (final answer): Based on the rubric and your evaluations in step 2, what should be the score of the story on the trait?
                    You should be generous and not too strict when evaluating.
                    Answer:
                """)
                reasoning, score = self._judge(
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                )
                aspect_overall_score += float(score) / len(HYPOEVAL_ASPECT_HYPOTHESIS_MAPPING[f"story_{aspect}"])
                aspect_overall_reasoning += f"----------Details for scoring for {aspect} aspect on the following decomposed dimension:\n{hypothesis}\nScore: {score}\nReasoning: {reasoning}\n"
            overall_score += f"Overall score on {aspect}: {round(aspect_overall_score, 1)}\n"
            overall_reasoning += f"==========Reasoning for aspect {aspect}:\n{aspect_overall_reasoning}\n"
        return Judgment(overall_score, overall_reasoning)