from pathlib import Path
from core import AutoJudge

# Path to the test dataset
dataset_path = "/Users/jamesliounis/Documents/judges/judges/autojudge/tests/data/synthetic_travel_qa.csv"

# Initialize AutoJudge
processor = AutoJudge(
)

try:
    # Run the full pipeline
    processor.run_pipeline(dataset_path)

    print("\nPipeline executed successfully.")
    print("Generated Rubric:")
    print(processor.rubric)

    # Test the judge method with sample input and output
    sample_input = "Where should I go for my honeymoon?"
    sample_output = "The moon, probably"

    print("\nTesting judge method...")
    judgment_result = processor.judge(
        input=sample_input,
        output=sample_output
    )

    # Print the judgment result
    print("\nJudgment Result:")
    print(f"Reasoning: {judgment_result.reasoning}")
    print(f"Score: {'Correct' if judgment_result.score else 'Incorrect'}")

except Exception as e:
    print(f"Error during execution: {e}")
