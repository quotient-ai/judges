# pip install "judges[auto]"

from judges.classifiers.auto import AutoJudge

dataset = [
    {
        "input": "Can I ride a dragon in Scotland?",
        "output": "Yes, dragons are commonly seen in the highlands and can be ridden with proper training.",
        "label": 0,
        "feedback": "Dragons are mythical creatures; the information is fictional.",
    },
    {
        "input": "Can you recommend a good hotel in Tokyo?",
        "output": "Certainly! Hotel Sunroute Plaza Shinjuku is highly rated for its location and amenities. It offers comfortable rooms and excellent service.",
        "label": 1,
        "feedback": "Offers a specific and helpful recommendation.",
    },
    {
        "input": "Can I drink tap water in London?",
        "output": "Yes, tap water in London is safe to drink and meets high quality standards.",
        "label": 1,
        "feedback": "Gives clear and reassuring information.",
    },
    {
        "input": "What's the boiling point of water on the moon?",
        "output": "The boiling point of water on the moon is 100°C, the same as on Earth.",
        "label": 0,
        "feedback": "Boiling point varies with pressure; the moon's vacuum affects it.",
    }
]


# Task description
task = "Evaluate responses for accuracy, clarity, and helpfulness."

# Initialize autojudge
autojudge = AutoJudge.from_dataset(
    dataset=dataset,
    task=task,
    model="gpt-4-turbo-2024-04-09",
    # increase workers for speed ⚡
    # max_workers=2,
    # generated prompts are automatically saved to disk
    # save_to_disk=False,
)

## Now judge new data

# Input-output pair to evaluate
input_ = "What are the top attractions in New York City?"
output = "Some top attractions in NYC include the Statue of Liberty and Central Park."

# Get the judgment
judgment = autojudge.judge(input=input_, output=output)

# Print the judgment
print(judgment.reasoning)
# The response accurately lists popular attractions like the Statue of Liberty and Central Park, which are well-known and relevant to the user's query.
print(judgment.score)
# True (correct)
