# NEW_FILE_PATH: /venvs/judges/source/judges/cli.py

import typer
import json
import os
from typing import List, Optional
from judges import choices_judges, get_judge_by_name
from pydantic import BaseModel, TypeAdapter, ConfigDict
app = typer.Typer()

class Sample(BaseModel):
    input: str
    output: str
    expected: Optional[str]

    model_config = ConfigDict(strict=True)

class Dataset(BaseModel):
    samples: List[Sample]


def parse_json_dict(json_dict: str) -> Dataset:
    """
    Parse a JSON dictionary or path to a JSON file into a Dataset object.
    Each sample must have 'input', 'output', and 'expected' keys.

    Args:
        json_dict: Either a JSON string or a path to a JSON file

    Returns:
        Dataset object containing Sample objects with 'input', 'output', and 'expected' fields

    Raises:
        ValueError: If the JSON is invalid or missing required keys
    """
    # Try to parse as JSON string first
    try:
        data = json.loads(json_dict)
    except json.JSONDecodeError:
        # If not a valid JSON string, try to read as file
        if not os.path.exists(json_dict):
            raise ValueError(f"Invalid JSON string and file not found: {json_dict}")
        try:
            with open(json_dict, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in file: {json_dict}")

    # Convert single dictionary to list
    if isinstance(data, dict):
        data = [data]

    # Validate format
    validated_entries = TypeAdapter(List[Sample]).validate_python(data)
    dataset = Dataset(samples=validated_entries)

    return dataset


@app.command()
def main(judge: choices_judges,
         model: str = typer.Option(..., "--model", "-m", help="The name of the model to use (e.g., 'gpt-4', '<provider>/<model_name>')"),
         input_json: str = typer.Option(..., "--input", "-i", help="Either a JSON string or path to a JSON file containing test cases"),
         output_json: str = typer.Option(None, "--output", "-o", help="Path to save the results (if not provided, prints to stdout)")):
    """
    Evaluate model outputs using specified judges and models.

    This function takes a judge type, model name, and JSON input (either as a string or file path)
    to evaluate model outputs against expected answers. The JSON input should contain one or more
    entries, each with 'input', 'output', and 'expected' keys.

    Args:
        judge (choices_judges): The type of judge to use for evaluation (e.g., CorrectnessPollKiltHotpot,
            EmotionQueenImplicitEmotionRecognition, etc.)
        model (str): The name of the model to use for the judge (e.g., "gpt-4", "claude-3-opus", etc.)
        input_json (str): Either a JSON string or path to a JSON file containing the test cases.
            Each test case must have 'input', 'output', and 'expected' keys.
            Example JSON format:
            {
                "input": "What is the capital of Germany?",
                "output": "The capital of Germany is Paris.",
                "expected": "The capital of Germany is Berlin."
            }
            Or for multiple test cases:
            [
                {
                    "input": "What is the capital of France?",
                    "output": "The capital of France is Madrid.",
                    "expected": "The capital of France is Paris."
                },
                {
                    "input": "What is the capital of Germany?",
                    "output": "The capital of Germany is Paris.",
                    "expected": "The capital of Germany is Berlin."
                }
            ]
        output_json (str): The path to the output file to save the results.
            If not provided, the results will be printed to stdout.

    Returns:
        None: Prints the judgment and reasoning for each test case to stdout.

    Raises:
        ValueError: If the JSON input is invalid or missing required keys.
        Exception: If there's an error processing any individual test case.
    """
    judge_constructor = get_judge_by_name(judge)
    judge = judge_constructor(model)
    results = []

    # Parse the JSON input
    try:
        entries = parse_json_dict(input_json)
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return

    # Process each entry
    for i, entry in enumerate(entries.samples):
        try:
            judgment = judge.judge(
                input=entry.input,
                output=entry.output,
                expected=entry.expected
            )
            results.append(
                {
                    "input": entry.input,
                    "output": entry.output,
                    "expected": entry.expected,
                    "judgment": judgment.score,
                    "reasoning": judgment.reasoning,
                }
            )
        except Exception as e:
            print(f"Error processing entry {i}: {e}")

    if output_json:
        with open(output_json, "w") as f:
            json.dump(results, f, indent=4)
        print(f"Results saved to {output_json}")
    else:
        print(json.dumps(results, indent=4))


if __name__ == "__main__":
    app()
