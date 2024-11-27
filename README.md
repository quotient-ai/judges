# judges ‍⚖️

1. [Overview](#overview)
2. [Installation](#installation)
3. [API](#api)
   - [Types of Judges](#types-of-judges)
     - [Classifiers](#classifiers)
     - [Graders](#graders)
   - [Using Judges](#using-judges)
     - [Classifier Judges](#classifier-judges)
   - [Combining Judges](#combining-judges)
     - [Jury Object](#jury-object)
4. [Usage](#usage)
   - [Set your OpenAI API key](#set-your-openai-api-key)
   - [Send data to an LLM](#send-data-to-an-llm)
   - [Use a `judges` classifier LLM as an evaluator model](#use-a-judges-classifier-llm-as-an-evaluator-model)
   - [Use a `Jury` for averaging and diversification](#use-a-jury-for-averaging-and-diversification)
5. [Appendix of Judges](#appendix)
   - [Classifiers](#classifiers) 
   - [Grader](#graders) 


## Overview
`judges` is a small library to use and create LLM-as-a-Judge evaluators. The purpose of `judges` is to have a curated set of LLM evaluators in a low-friction format across a variety of use cases that are backed by research, and can be used off-the-shelf or serve as inspiration for building your own LLM evaluators.

## Installation
```
pip install judges
```

## API

### Types of Judges

The library provides two types of judges:

1. **Classifiers**: Return boolean values.
   - `True` indicates the inputs passed the evaluation.
   - `False` indicates the inputs did not pass the evaluation.

2. **Graders**: Return scores on a numerical or Likert scale.
   - Numerical scale: 1 to 5
   - Likert scale: terrible, bad, average, good, excellent

### Using Judges

All judges can be used by calling the `.judge()` method. This method accepts the following parameters:
- `input`: The input to be evaluated.
- `output`: The output to be evaluated.
- `expected` (optional): The expected result for comparison.

The `.judge()` method returns a `Judgment` object with the following attributes:
- `reasoning`: The reasoning behind the judgment.
- `score`: The score assigned by the judge.

### Classifier Judges

If the underlying prompt for a classifier judge outputs a `Judgment` similar to `True` or `False` (e.g., good or bad, yes or no, 0 or 1), the `judges` library automatically resolves the outputs so that a `Judgment` only has a boolean label.

### Combining Judges

The library also provides an interface to combine multiple judges through the `Jury` object. The `Jury` object has a `.vote()` method that produces a `Verdict`.

### Jury Object

- `.vote()`: Combines the judgments of multiple judges and produces a `Verdict`.

## Usage

1. Set your OpenAI API key
To get started, you'll need an OpenAI API key set as an environment variable `OPENAI_API_KEY`

Next, if you'd like to use this package, you can follow the `example.py` below:

2. Send data to an LLM
```python
from openai import OpenAI

client = OpenAI()

question = "What is the name of the rabbit in the following story. Respond with 'I don't know' if you don't know."

story = """
Fig was a small, scruffy dog with a big personality. He lived in a quiet little town where everyone knew his name. Fig loved adventures, and every day he would roam the neighborhood, wagging his tail and sniffing out new things to explore.

One day, Fig discovered a mysterious trail of footprints leading into the woods. Curiosity got the best of him, and he followed them deep into the trees. As he trotted along, he heard rustling in the bushes and suddenly, out popped a rabbit! The rabbit looked at Fig with wide eyes and darted off.

But instead of chasing it, Fig barked in excitement, as if saying, “Nice to meet you!” The rabbit stopped, surprised, and came back. They sat together for a moment, sharing the calm of the woods.

From that day on, Fig had a new friend. Every afternoon, the two of them would meet in the same spot, enjoying the quiet companionship of an unlikely friendship. Fig's adventurous heart had found a little peace in the simple joy of being with his new friend.
"""

# set up the input prompt
input = f'{story}\n\nQuestion:{question}'

# write down what the model is expected to respond with
expected = "I don't know"

# get the model output
output = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {
            'role': 'user', 
            'content': input,
        },
    ],
).choices[0].message.content
```

3a. Use a `judges` classifier LLM as an evaluator model

```python
from judges.classifiers.correctness import PollMultihopCorrectness

# use the correctness classifier to determine if the first model
# answered correctly
correctness = PollMultihopCorrectness(model='gpt-4o-mini')

judgment = correctness.judge(
    input=input,
    output=output,
    expected=expected,
)
print(judgment.reasoning)
# The 'Answer' provided ('I don't know') matches the 'Reference' text which also states 'I don't know'. Therefore, the 'Answer' correctly corresponds with the information given in the 'Reference'.

print(judgment.score)
# True
```

3b. Use a `Jury` for averaging and diversification

A jury of LLMs can enable more diverse results and enable you to combine the judgments of multiple LLMs.

```python
from judges import Jury
from judges.classifiers.correctness import PollMultihopCorrectness, RAFTCorrectness

poll = PollMultihopCorrectness(model='gpt-4o')
raft = RAFTCorrectness(model='gpt-4o-mini')

jury = Jury(judges=[poll, raft], voting_method="average")

verdict = jury.vote(
    input=input,
    output=completion,
    expected=expected,
)
print(verdict.score)
```

## Appendix

### Classifiers

| Judge Type | Category                 | Description                                                                                                                                                                                                                                                                                                                                                                                                                                  | Reference Paper                                                                                                                                                                                                                                                                                   | Python Import                                                                                                                           |
|------------|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| classifier | Factual Correctness      | Evaluates the factual correctness of a generated response against a reference answer using few-shot learning. It compares the provided answer with the reference answer to determine its accuracy.                                                                                                                                                                                                                                                 | [Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models](https://arxiv.org/abs/2404.18796)                                                                                                                                                             | ```from judges.classifiers.correctness import PollMultihopCorrectness```                                               |
| classifier | Factual Correctness      | Assesses the factual accuracy of an AI assistant's response against a reference answer without relying on example-based (few-shot) learning. It determines whether the provided answer aligns with the reference answer based on factual information.                                                                                                                                                                                         | [Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models](https://arxiv.org/abs/2404.18796)                                                                                                                                                             | ```from judges.classifiers.correctness import PollZeroShotCorrectness```                                               |
| classifier | Factual Correctness      | Evaluates the factual correctness of responses based on the KILT (Knowledge Intensive Language Tasks) version of Natural Questions. It uses few-shot learning to compare the AI assistant's response with the reference answer to assess accuracy.                                                                                                                                                                                         | [Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models](https://arxiv.org/abs/2404.18796)                                                                                                                                                             | ```from judges.classifiers.correctness import PollKiltNQCorrectness```                                                 |
| classifier | Factual Correctness      | Assesses the factual correctness of responses based on the KILT version of HotpotQA. It utilizes few-shot learning to determine whether the AI assistant's response aligns with the reference answer, ensuring accuracy and consistency.                                                                                                                                                                                                  | [Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models](https://arxiv.org/abs/2404.18796)                                                                                                                                                             | ```from judges.classifiers.correctness import PollKiltHotpotCorrectness```                                             |
| classifier | Factual Correctness      | Evaluates the factual correctness of responses using LLAMA-based methods as part of the RAFT (Adapting Language Model to Domain Specific RAG) framework. It determines the accuracy of the AI assistant's response by comparing it with the reference answer based on predefined criteria.                                                                                                                                                             | [RAFT: Adapting Language Model to Domain Specific RAG](https://arxiv.org/abs/2403.10131)                                                                                                                                                                                           | ```from judges.classifiers.correctness import RAFTCorrectness```                                                        |
| classifier | Hallucination Evaluation | Determines whether a provided answer contains non-factual or hallucinated information based on predefined hallucination types and world knowledge. It evaluates the factual integrity of the AI assistant's response to ensure accuracy and reliability.                                                                                                                                                                                   | [HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models](https://arxiv.org/abs/2305.11747)                                                                                                                                                            | ```from judges.classifiers.correctness.hallucination import HaluEvalAnswerNonFactual```                                            |
| classifier | Hallucination Evaluation | Evaluates whether a dialogue response contains non-factual or hallucinated information by analyzing the response against predefined hallucination types and world knowledge. It ensures that the AI assistant's responses are factually accurate within the context of the dialogue.                                                                                                                                                         | [HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models](https://arxiv.org/abs/2305.11747)                                                                                                                                                            | ```from judges.classifiers.correctness.hallucination import HaluEvalDialogueResponseNonFactual```                                  |
| classifier | Hallucination Evaluation | Assesses whether a document summary contains non-factual or hallucinated information by comparing it against the source document. It ensures the summary accurately reflects the content without introducing incorrect or fabricated details.                                                                                                                                                                                             | [HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models](https://arxiv.org/abs/2305.11747)                                                                                                                                                            | ```from judges.classifiers.correctness.hallucination import HaluEvalDocumentSummaryNonFactual```                                   |
| classifier | Content Categorization   | Categorizes user input texts into predefined categories such as hate, self-harm, sexual content, violence, harassment, harmful, illegal, unethical, privacy, deception, or none of the above. Ensures that content is not categorized if it's solely for knowledge understanding without intent to commit or promote the activities.                                                                                                                             | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)                                                                                                                                                                                     | ```from judges.classifiers.correctness.poll_content_category_correctness import PollContentCategoryCorrectness```                   |
| classifier | Response Type Classification | Classifies AI assistant responses into one of three classes: `direct_answer`, `direct_refusal`, or `indirect_refusal`. Evaluates whether the assistant provides a direct response, refuses to answer, or offers an alternative without addressing the original query directly.                                                                                                                                                                         | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)                                                                                                                                                                                     | ```from judges.classifiers.correctness.poll_response_type_classification_correctness import PollResponseTypeClassificationCorrectness``` |
| classifier | Extended Content Categorization | Extends content categorization into eleven specific categories, providing a more granular classification framework. Evaluates whether user inputs fall into categories such as hate, self-harm, sexual, violence, harassment, harmful, illegal, unethical, privacy, deception, or none of the above, ensuring accurate classification based on intent and content nature.                                                                                                         | [OR-Bench: An Over-Refusal Benchmark for Large Language Models](https://arxiv.org/abs/2405.20947)                                                                                                                                                                               | ```from judges.classifiers.correctness.poll_content_category_extended_correctness import PollContentCategoryExtendedCorrectness```     |
| classifier | Harmfulness Evaluation   | Evaluates whether an AI assistant's response contains harmful content, including harmful, dangerous, unethical, illegal, or hostile information. It assesses the response for alignment with trustworthy language model guidelines to ensure the safety and reliability of the output.                                                                                                                                                                          | [Trustworthy LLMs: a Survey and Guideline for Evaluating Large Language Models' Alignment](https://arxiv.org/abs/2308.05374)                                                                                                                                                     | ```from judges.classifiers.correctness.harmfulness import TrustworthyLLMHarmfulness```                                           |
| classifier | Query Quality Evaluation | Evaluates the quality of a query based on clarity, specificity, and relevance. It assesses whether the query is well-structured and aligned with the desired information retrieval objectives, ensuring that the queries facilitate accurate and relevant responses from the AI assistant.                                                                                                                                                                        | [FactAlign: Long-form Factuality Alignment of Large Language Models](https://arxiv.org/abs/2410.01691)                                                                                                                                                                              | ```from judges.classifiers.query_quality import FactAlignQueryQuality```                                               |
| classifier | Refusal Evaluation       | Evaluates whether an AI assistant's response refuses to complete a given task. It determines if the response is a refusal based on predefined criteria, ensuring that the AI adheres to ethical guidelines and alignment policies when declining to assist with certain requests.                                                                                                                                                                         | [Trustworthy LLMs: a Survey and Guideline for Evaluating Large Language Models' Alignment](https://arxiv.org/abs/2308.05374)                                                                                                                                                     | ```from judges.classifiers.correctness.refusal import TrustworthyLLMRefusal```                                                   |

---


### Graders

| Judge Type | Category                       | Description                                                                                                                                                                                                                                                                                                                                                                                                                              | Reference Paper                                                                                                                                                             | Python Import                                                                                                                           |
|------------|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| grader     | Factual Correctness            | Evaluates the correctness of a response in an Absolute Grading setting, according to a scoring rubric.                                                                                                                                                                                                                                                                                                                                 | [Prometheus: Inducing Fine-grained Evaluation Capability in Language Models](https://arxiv.org/abs/2310.08491)                                                               | `from judges.graders.correctness import PrometheusAbsoluteCoarseCorrectness`                                                        |
| grader     | Empathy Evaluation             | Evaluates the response of a model based on its ability to recognize implicit emotions in a statement, using a 3-point scale.                                                                                                                                                                                                                                                                                                                  | [EmotionQueen: A Benchmark for Evaluating Empathy of Large Language Models](https://arxiv.org/abs/2409.13359)                                                             | `from judges.graders.empathy import EmotionQueenImplicitEmotionRecognition`                                                          |
| grader     | Empathy Evaluation             | Evaluates the response of a model based on its ability to recognize the hidden intention in a statement, using a 3-point scale.                                                                                                                                                                                                                                                                                                                   | [EmotionQueen: A Benchmark for Evaluating Empathy of Large Language Models](https://arxiv.org/abs/2409.13359)                                                             | `from judges.graders.empathy import EmotionQueenIntentionRecognition`                                                               |
| grader     | Empathy Evaluation             | Evaluates the response of a model based on its ability to recognize the key event in a statement, using a 3-point scale.                                                                                                                                                                                                                                                                                                                              | [EmotionQueen: A Benchmark for Evaluating Empathy of Large Language Models](https://arxiv.org/abs/2409.13359)                                                             | `from judges.graders.empathy import EmotionQueenKeyEventRecognition`                                                                 |
| grader     | Empathy Evaluation             | Evaluates the response of a model based on its ability to recognize both the significant and trivial events in a statement, using a 3-point scale.                                                                                                                                                                                                                                                                                                | [EmotionQueen: A Benchmark for Evaluating Empathy of Large Language Models](https://arxiv.org/abs/2409.13359)                                                             | `from judges.graders.empathy import EmotionQueenMixedEventRecognition`                                                               |
| grader     | Information Coverage Evaluation | Determines whether a specific reference insight is fully, partially, or not covered within a provided list of bullet points, ensuring comprehensive coverage of key information.                                                                                                                                                                                                                                                                 | [Summary of a Haystack: A Challenge to Long-Context LLMs and RAG Systems](https://arxiv.org/abs/2407.01370)                                                                 | `from judges.graders.information_coverage import HaystackBulletPointCoverageCorrectness`                                               |
| grader     | Content Moderation             | Categorizes user input texts into predefined categories such as hate, self-harm, sexual content, etc., determining the appropriate category based on the content's nature and intent.                                                                                                                                                                                                                                                       | [OR-Bench: An Over-Refusal Benchmark for Large Language Models](https://arxiv.org/abs/2405.20947)                                                                        | `from judges.graders.moderator import ORBenchUserInputModeration`                                                                   |
| grader     | Content Moderation             | Classifies model output texts into one of eleven predefined categories related to content sensitivity and appropriateness, ensuring responses adhere to ethical and safety guidelines.                                                                                                                                                                                                                                                 | [OR-Bench: An Over-Refusal Benchmark for Large Language Models](https://arxiv.org/abs/2405.20947)                                                                        | `from judges.graders.moderator import ORBenchUserOutputModeration`                                                                  |
| grader     | Query Quality Evaluation       | Assesses the quality of user queries based on clarity, specificity, and coherence, ensuring that queries are well-structured to facilitate accurate and relevant responses.                                                                                                                                                                                                                                                                  | [Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing](https://api.semanticscholar.org/CorpusID:270391432)                                   | `from judges.graders.query_quality import MagpieQueryQuality`                                                                         |
| grader     | Refusal Evaluation             | Classifies AI assistant responses into direct_answer, direct_refusal, or indirect_refusal, evaluating whether the assistant appropriately refuses to answer certain prompts based on ethical guidelines.                                                                                                                                                                                                                                         | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)                                                                               | `from judges.graders.refusal_detection import ORBenchRefusalDetection`                                                                 |
| grader     | Relevance Evaluation           | Evaluates the relevance of a passage to a query based on a four-point scale: Irrelevant, Related, Highly relevant, Perfectly relevant. Ensures that the passage adequately addresses the query with varying degrees of relevance.                                                                                                                                                                                                          | [Reliable Confidence Intervals for Information Retrieval Evaluation Using Generative A.I.](https://doi.org/10.1145/3637528.3671883)                                         | `from judges.graders.relevance import ReliableCIRelevance`                                                                             |
| grader     | Response Quality Evaluation    | Evaluates the quality of the AI assistant's response based on helpfulness, relevance, accuracy, depth, creativity, and level of detail, assigning a numerical grade.                                                                                                                                                                                                                                                                      | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)                                                                               | `from judges.graders.response_quality import MTBenchChatBotResponseQuality`                                                            |

---
