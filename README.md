# judges

## Overview
A small library to use and create LLM-as-a-Judge evaluators.

## Installation
```
pip install judges
```

## Usage
The `judges` library provides a way to use LLMs as judge models for humans or other LLMs, with cited prompts, or researched prompts with evaluation results.

The library exposes to kinds of built-in judges:

- `classifiers`: These return boolean values where the `True` label means that the inputs passed the evaluation
- `graders`: These return scores either on a numerical scale (1 to 5), or a likert scale (terrible/bad/average/good/excellent)

## API

If you'd like to use this package, you can follow the `example.py` below:

### Send data to an LLM
```python
from openai import OpenAI

client = OpenAI()

question = "What is the name of the rabbit in the following story Respond with 'I don't know' if you don't know."

story = """
Fig was a small, scruffy dog with a big personality. He lived in a quiet little town where everyone knew his name. Fig loved adventures, and every day he would roam the neighborhood, wagging his tail and sniffing out new things to explore.

One day, Fig discovered a mysterious trail of footprints leading into the woods. Curiosity got the best of him, and he followed them deep into the trees. As he trotted along, he heard rustling in the bushes and suddenly, out popped a rabbit! The rabbit looked at Fig with wide eyes and darted off.

But instead of chasing it, Fig barked in excitement, as if saying, “Nice to meet you!” The rabbit stopped, surprised, and came back. They sat together for a moment, sharing the calm of the woods.

From that day on, Fig had a new friend. Every afternoon, the two of them would meet in the same spot, enjoying the quiet companionship of an unlikely friendship. Fig's adventurous heart had found a little peace in the simple joy of being with his new friend.
"""

# set up the input prompt
input = f'{story}\n\nQuestion:{question}'
# write down what I expect the model to respond with
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

### Use a `judges` classifier LLM as an evaluator model
```python
from judges.classifiers import AnswerCorrectness

# use the correctness classifier to determine if the first model
# answered correctly
correctness = AnswerCorrectness(model='gpt-4o')
verdict = correctness.judge(
    input=input,
    output=completion,
    expected=expected,
)
print(verdict.reasoning)
# The 'Answer' provided ('I don't know') matches the 'Reference' text which also states 'I don't know'. Therefore, the 'Answer' correctly corresponds with the information given in the 'Reference'.

print(verdict.score)
True
```

### Build an LLM-as-a-Judge