# NEW_FILE_PATH: /venvs/judges/source/judges/cli.py

import typer
import json
import os
from typing import Dict, List
from judges import choices_judges, get_judge_by_name

app = typer.Typer()


def parse_json_dict(json_dict: str) -> List[Dict[str, str]]:
    """
    Parse a JSON dictionary or path to a JSON file into a list of dictionaries.
    Each dictionary must have 'input', 'output', and 'expected' keys.

    Args:
        json_dict: Either a JSON string or a path to a JSON file

    Returns:
        List of dictionaries with 'input', 'output', and 'expected' keys

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
    required_keys = {"input", "output", "expected"}
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry {i} is not a dictionary")

        # Check for missing keys
        missing_keys = required_keys - set(entry.keys())
        if missing_keys:
            raise ValueError(f"Entry {i} is missing required keys: {missing_keys}")

        # Check for empty strings
        for key in required_keys:
            if entry[key] == "":
                print(f"Warning: Empty string found for key '{key}' in entry {i}")

    return data


@app.command()
def main(judge: choices_judges, model_name: str, json_dict: str, out: str = None):
    """
    Evaluate model outputs using specified judges and models.

    This function takes a judge type, model name, and JSON input (either as a string or file path)
    to evaluate model outputs against expected answers. The JSON input should contain one or more
    entries, each with 'input', 'output', and 'expected' keys.

    Args:
        judge (choices_judges): The type of judge to use for evaluation (e.g., CorrectnessPollKiltHotpot,
            EmotionQueenImplicitEmotionRecognition, etc.)
        model_name (str): The name of the model to use for the judge (e.g., "gpt-4", "claude-3-opus", etc.)
        json_dict (str): Either a JSON string or path to a JSON file containing the test cases.
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
        out (str): The path to the output file to save the results.
            If not provided, the results will be printed to stdout.

    Returns:
        None: Prints the judgement and reasoning for each test case to stdout.

    Raises:
        ValueError: If the JSON input is invalid or missing required keys.
        Exception: If there's an error processing any individual test case.
    """
    judge_constructor = get_judge_by_name(judge)
    judge = judge_constructor(model_name)
    results = []

    # Parse the JSON input
    try:
        entries = parse_json_dict(json_dict)
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return

    # Process each entry
    for i, entry in enumerate(entries):
        try:
            judgement = judge.judge(
                input=entry["input"],
                output=entry["output"],
                expected=entry["expected"]
            )
            results.append(
                {
                    "input": entry["input"],
                    "output": entry["output"],
                    "expected": entry["expected"],
                    "judgement": judgement.score,
                    "reasoning": judgement.reasoning,
                }
            )
        except Exception as e:
            print(f"Error processing entry {i}: {e}")

    if out:
        with open(out, "w") as f:
            json.dump(results, f, indent=4)
        print(f"Results saved to {out}")
    else:
        print(json.dumps(results, indent=4))


if __name__ == "__main__":
    app()
