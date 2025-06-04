from openai import OpenAI

client = OpenAI()

question = "What is the name of the rabbit in the following story. Respond with 'I don't know' if you don't know."

story = """
Fig was a small, scruffy dog with a big personality. He lived in a quiet little town where everyone knew his name. Fig loved adventures, and every day he would roam the neighborhood, wagging his tail and sniffing out new things to explore.

One day, Fig discovered a mysterious trail of footprints leading into the woods. Curiosity got the best of him, and he followed them deep into the trees. As he trotted along, he heard rustling in the bushes and suddenly, out popped a rabbit! The rabbit looked at Fig with wide eyes and darted off.

But instead of chasing it, Fig barked in excitement, as if saying, “Nice to meet you!” The rabbit stopped, surprised, and came back. They sat together for a moment, sharing the calm of the woods.

From that day on, Fig had a new friend. Every afternoon, the two of them would meet in the same spot, enjoying the quiet companionship of an unlikely friendship. Fig's adventurous heart had found a little peace in the simple joy of being with his new friend.
"""

print("Getting input, expected, and output...")
# set up the input prompt
input = f'{story}\n\nQuestion:{question}'

# write down what the model is expected to respond with
# NOTE: not all judges require an expected answer. refer to the implementations
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


from judges import Jury
from judges.classifiers.correctness import PollMultihopCorrectness, RAFTCorrectness, PollZeroShotCorrectness

poll = PollMultihopCorrectness(model='anthropic/claude-sonnet-4-20250514')
raft = RAFTCorrectness(model='openai/gpt-4o-mini')
poll_zeroshot = PollZeroShotCorrectness('openai/gpt-4.1')

jury = Jury(judges=[poll, raft, poll_zeroshot], voting_method="average")

print("Getting jury's verdict...")
verdict = jury.vote(
    input=input,
    output=output,
    expected=expected,
)
print("Verdict:")
print(verdict.score)
print("--------------------------------")
print("Individual Judgments:")
for i, judgment in enumerate(verdict.judgments):
    print(f"Judgment {i+1}:")
    print(judgment.reasoning)
    print(judgment.score)
    print("--------------------------------")
print("--------------------------------")

