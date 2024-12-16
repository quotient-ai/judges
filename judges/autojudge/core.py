import json
import os
import csv
import logging
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Union, Optional

from judges.base import BaseJudge, Judgment
from autojudge.engine.llm_engine import LLMRecommendationEngine
from autojudge.metrics.compute_metrics import ComputeMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

class Autojudge(BaseJudge):
    """
    Autojudge class that:
    1. Takes user-provided data and a task description.
    2. Generates a rubric from aggregated and structured feedback derived from the data.
    3. Computes metrics to evaluate the rubric's performance on the provided dataset.
    4. Uses the rubric to judge new input-output pairs, returning a Judgment.
    """

    def __init__(self, model: str):
        super().__init__(model=model)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm_engine = LLMRecommendationEngine()
        self.rubric = ""
        self.structured_feedback = ""
        self.metrics = {}
        self.data: List[Dict[str, Union[str, int]]] = []
        self.task_description = ""
        self.prompts_dir = Path(__file__).parent / "prompts"

    def load_data(self, dataset: Union[str, Path, List[Dict[str, Union[str, int]]]]):
        if isinstance(dataset, (str, Path)):
            dataset_path = Path(dataset)
            self.logger.info(f"Loading data from {dataset_path}")
            with dataset_path.open('r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.data = [row for row in reader]
            self.logger.info(f"Data loaded successfully with {len(self.data)} records.")
        elif isinstance(dataset, list):
            self.data = dataset
            self.logger.info(f"Data loaded from a list with {len(self.data)} records.")
        else:
            raise TypeError("Dataset must be a file path or a list of dictionaries.")

    def aggregate_feedback(self) -> str:
        bad_data_points = [row for row in self.data if int(row.get('label', 0)) == 0]
        if not bad_data_points:
            self.logger.warning("No bad data points found with label=0.")
            return ""
        aggregated_feedback = ' - ' + '\n - '.join(
            row['feedback'] for row in bad_data_points if row.get('feedback')
        )
        return aggregated_feedback

    def load_prompt(self, prompt_filename: str) -> str:
        prompt_path = self.prompts_dir / prompt_filename
        with prompt_path.open('r', encoding='utf-8') as file:
            return file.read()

    def generate_structured_feedback(self, task_description: str, feedback: str) -> str:
        try:
            structure_feedback_prompt = self.load_prompt('STRUCTURE_FEEDBACK.txt')
            formatted_prompt = structure_feedback_prompt.format(task=task_description, feedback=feedback)
            response = self.llm_engine.get_llm_completion(
                formatted_prompt,
                temperature=0.1
            )
            structured_content = response.choices[0].message.content.strip()
            return structured_content
        except Exception as e:
            self.logger.error(f"Error generating structured feedback: {e}")
            raise

    def generate_grading_notes(self, structured_feedback: str, task_description: str) -> str:
        try:
            generate_grading_note_prompt = self.load_prompt('GENERATE_GRADING_NOTE.txt')
            grading_note_format_instructions = self.load_prompt('GRADING_NOTE_FORMAT.txt')

            formatted_prompt = generate_grading_note_prompt.format(
                feedback=structured_feedback,
                task=task_description
            )
            grading_notes_completion = self.llm_engine.get_llm_completion(
                formatted_prompt,
                temperature=0
            )
            grading_notes = grading_notes_completion.choices[0].message.content.strip()

            grading_notes += "\n\n" + grading_note_format_instructions
            return grading_notes
        except Exception as e:
            self.logger.error(f"Error generating grading notes: {e}")
            raise

    def evaluate_rubric(self) -> dict:
        true_labels = [int(row['label']) for row in self.data]
        predicted_labels = []

        for idx, row in enumerate(self.data):
            output = row.get('completion', '')
            input_str = row.get('input_text', '')

            if not output:
                predicted_labels.append(0)
                continue

            user_prompt = dedent(f"""
            {self.rubric}

            ### Input ###
            {input_str}

            ### Output ###
            {output}

            ### Evaluation ###
            """)

            print(user_prompt)

            # Print the prompt for debugging
            print(f"\n[DEBUG] Prompt for data point {idx}:\n{user_prompt}")

            try:
                grading_note = self.llm_engine.get_llm_completion(
                    user_prompt,
                    model=self.model,
                    temperature=0
                )
                response_content = grading_note.choices[0].message.content.strip()

                # Print the raw response before parsing JSON
                print(f"[DEBUG] Raw LLM response for data point {idx}: {response_content}")

                # Basic validation check to see if it looks like JSON
                if not (response_content.startswith('{') and response_content.endswith('}')):
                    self.logger.error(f"Response does not look like JSON for data point {idx}:\n{response_content}")
                    predicted_labels.append(0)
                    continue

                try:
                    data = json.loads(response_content)
                except json.JSONDecodeError as json_err:
                    self.logger.error(f"Error applying rubric to a data point (JSONDecodeError): {json_err}")
                    print(f"[ERROR] JSON parsing failed for data point {idx}. Response content was:\n{response_content}")
                    predicted_labels.append(0)
                    continue

                # Once parsed successfully
                print(data)
                score = data.get("SCORE", False)
                reasoning = data.get("REASONING", "")
                classification = 1 if score else 0
                predicted_labels.append(classification)

            except Exception as e:
                self.logger.error(f"Error applying rubric to a data point: {e}")
                predicted_labels.append(0)

        compute_metrics = ComputeMetrics(true_labels, predicted_labels)
        metrics = {
            "Cohen's kappa": compute_metrics.calculate_kappa(),
            "Accuracy": compute_metrics.calculate_accuracy(),
            "Precision": compute_metrics.calculate_precision(),
            "Recall": compute_metrics.calculate_recall(),
            "F1 Score": compute_metrics.calculate_f1()
        }
        return metrics



    def generate_rubric(self, task_description: str, data: Union[str, Path, List[Dict[str, Union[str, int]]]]) -> Dict[str, Union[str, dict]]:
        self.task_description = task_description
        self.load_data(data)
        aggregated_feedback = self.aggregate_feedback()

        if not aggregated_feedback:
            self.logger.warning("No feedback to process. Rubric might be empty.")
            self.structured_feedback = ""
            self.rubric = ""
            self.metrics = {}
            return {"rubric": self.rubric, "metrics": self.metrics}

        self.structured_feedback = self.generate_structured_feedback(task_description, aggregated_feedback)
        self.rubric = self.generate_grading_notes(self.structured_feedback, task_description)
        
        print("[DEBUG] Generated Rubric:\n", self.rubric)
        
        self.metrics = self.evaluate_rubric()

        return {"rubric": self.rubric, "metrics": self.metrics}

    def judge(
        self,
        input: str,
        output: str = None,
        expected: str = None,
    ) -> Judgment:
        if not self.rubric:
            raise ValueError("Rubric not generated. Please call generate_rubric first.")

        user_prompt = dedent(f"""
        {self.rubric}

        ### Input ###
        {input}

        ### Output ###
        {output}

        ### Evaluation ###
        """)

        # Print the prompt used for the single judgment
        print("[DEBUG] Judge method prompt:\n", user_prompt)

        reasoning, score = self._judge(
            user_prompt=user_prompt,
            system_prompt=None,
        )
        
        # Print the reasoning and score
        print(f"[DEBUG] Reasoning: {reasoning}")
        print(f"[DEBUG] Score: {score}")

        return Judgment(reasoning=reasoning, score=score)
