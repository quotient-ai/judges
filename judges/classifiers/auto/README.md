# `autojudge`: Personalized Evaluation for AI Outputs  

## Overview  
`autojudge` is a novel extension to the **judges** library, designed to simplify and enhance the evaluation of AI-generated outputs. By leveraging labeled datasets with user-provided feedback, `autojudge` creates custom, task-specific evaluation systems tailored to your unique needs. This process is fully automated and scalable, offering a seamless way to evaluate AI models for accuracy, relevance, and clarity.  

`autojudge` eliminates the "one-size-fits-all" problem of generic evaluators, enabling you to generate precise, feedback-informed rubrics and personalized judge models. Whether you're working on chatbots, QA systems, or other LLM-based applications, `autojudge` bridges the gap between generic evaluations and nuanced, human-aligned assessments.

---

## Benefits  

1. **Custom, Feedback-Informed Evaluators**: `autojudge` combines user feedback with LLM capabilities to generate task-specific rubrics that align with real-world evaluation criteria.  
2. **Scalable and Efficient**: `autojudge` performs evaluations at scale with minimal labeled data, significantly reducing manual overhead.  
3. **Flexible and Adaptable**: Tailored evaluation systems adapt to domain-specific needs, ensuring consistency across datasets and use cases.  
4. **Insightful Metrics**: Measure performance using comprehensive evaluation metrics like accuracy, F1 scores, and Cohen’s kappa to align with human judgments.  

---

## How to Use `autojudge`  

### Installation  
`autojudge` is included in the **judges** library. Install it using:  
```bash
pip install judges
```  

### Preparing Your Dataset  
Your dataset should be a CSV file with the following columns:  
- **`input`**: The input or question being evaluated.  
- **`output`**: The AI's response.  
- **`label`**: Ground-truth labels (e.g., `1` for correct, `0` for incorrect).  
- **`feedback`**: Feedback explaining why the response is correct or incorrect.  

Example:  

| input                             | output                                                              | label | feedback                              |
|-----------------------------------|---------------------------------------------------------------------|-------|---------------------------------------|
| What's the best time to visit Paris? | The best time to visit Paris is during the spring or fall.          | 1     | Provides accurate and detailed advice. |

---

### Code Tutorial  

#### Step 1: Initialize `autojudge`  
Provide a labeled dataset and describe the evaluation task.  

```python
from judges import autojudge

# Path to your dataset
dataset_path = "./data/synthetic_travel_qa.csv"

# Task description
task_description = "Evaluate responses for accuracy, clarity, and helpfulness."

# Initialize autojudge
autojudge = autijduge.from_dataset(
    dataset=dataset_path,
    task=task_description,
    model="gpt-4-turbo-2024-04-09",  # Specify the LLM model
    max_workers=2,                   # Parallel processing for efficiency
)
```

---

#### Step 2: Evaluate an Input-Output Pair  
You can use `autojudge` to evaluate a single input-output pair using the `.judge()` method.  

```python
# Input-output pair to evaluate
input_text = "What are the top attractions in New York City?"
output_text = "Some top attractions in NYC include the Statue of Liberty and Central Park."

# Get the judgment
judgment = autojudge.judge(input=input_text, output=output_text)

# Print the judgment
print("Judgment Reasoning:", judgment.reasoning)
print("Judgment Score:", judgment.score)
```

**Expected Output**:  
```plaintext
Judgment Reasoning: The response accurately lists popular attractions like the Statue of Liberty and Central Park, which are well-known and relevant to the user's query.
Judgment Score: 1
```

---