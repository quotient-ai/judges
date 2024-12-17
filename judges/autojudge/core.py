from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from tqdm import tqdm
from pathlib import Path
import logging
from typing import Optional, Union, List, Dict
from metrics.compute_metrics import ComputeMetrics
from engine.llm_engine import LLMRecommendationEngine, GradingNote
import os
import json
from textwrap import dedent
from judges.base import BaseJudge, Judgment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)


class AutoJudge(BaseJudge):
    """
    A robust pipeline for evaluating AI-generated responses using a structured rubric,
    grading notes, and metrics like accuracy and Cohen's kappa.
    Inherits from BaseJudge for judging capabilities.
    """

    def __init__(
        self,
        prompts_dir: Optional[str] = "./prompts",
        grading_notes_dir: Optional[str] = "/tmp/grading_notes",
        max_rows: Optional[int] = None,
        llm_engine: Optional[LLMRecommendationEngine] = None,
        model: str = "gpt-4o-mini",  # Default model name
    ):
        """
        Initialize AutoJudge with configuration options.

        Args:
            prompts_dir (Optional[str]): Path to the directory containing LLM prompt templates.
            grading_notes_dir (Optional[str]): Path to the directory to save grading notes.
            max_rows (Optional[int]): Maximum number of rows to process for testing purposes.
            llm_engine (Optional[LLMRecommendationEngine]): Optional custom LLM engine instance.
            model (str): Name of the LLM model used for evaluation.
        """
        super().__init__(model=model)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Set directories
        self.prompts_dir = Path(prompts_dir).resolve()
        self.grading_notes_dir = Path(grading_notes_dir)
        self.grading_notes_dir.mkdir(parents=True, exist_ok=True)

        self.max_rows = max_rows
        self.llm_engine = llm_engine or LLMRecommendationEngine()
        self.grading_notes: str = ""
        self.data = []
        self.generated_grading_note_evals: List[GradingNote] = []

    def load_data(
        self, dataset: Union[str, Path, List[Dict[str, Union[str, int]]]]
    ) -> List[Dict[str, Union[str, int]]]:
        """
        Load data from a CSV file or a list of dictionaries.

        Args:
            dataset (Union[str, Path, List[Dict[str, Union[str, int]]]]): Path to CSV file or list of dictionaries.

        Returns:
            List[Dict[str, Union[str, int]]]: Loaded data rows as dictionaries.
        """
        try:
            self.logger.info("Loading dataset...")
            if isinstance(dataset, (str, Path)):
                dataset_path = Path(dataset)
                with dataset_path.open("r", encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    self.data = [
                        row
                        for idx, row in enumerate(reader)
                        if not self.max_rows or idx < self.max_rows
                    ]
            elif isinstance(dataset, list):
                self.data = dataset[: self.max_rows] if self.max_rows else dataset
            else:
                raise TypeError(
                    "Dataset must be a file path or a list of dictionaries."
                )

            if not self.data:
                raise ValueError("Loaded dataset is empty.")

            self.logger.info(f"Data loaded successfully with {len(self.data)} records.")
            return self.data
        except Exception as e:
            self.logger.error(f"Error loading dataset: {e}")
            raise

    def load_prompt(self, prompt_filename: str) -> str:
        """
        Load a specific LLM prompt template from the prompts directory.

        Args:
            prompt_filename (str): Name of the prompt file.

        Returns:
            str: The content of the prompt file.
        """
        try:
            prompt_path = self.prompts_dir / prompt_filename
            self.logger.info(f"Loading prompt from {prompt_path}")
            with prompt_path.open("r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            self.logger.error(f"Prompt file not found: {prompt_filename}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading prompt {prompt_filename}: {e}")
            raise

    def aggregate_feedback(self, data: List[Dict]) -> str:
        """
        Aggregate feedback from records with label=0.

        Args:
            data (List[Dict]): List of data records containing feedback.

        Returns:
            str: Aggregated feedback formatted as a bullet list.
        """
        try:
            self.logger.info("Aggregating feedback from bad data points...")
            bad_feedback = [
                row["feedback"]
                for row in data
                if str(row.get("label", "0")) == "0" and row.get("feedback")
            ]
            if not bad_feedback:
                self.logger.warning("No bad data points found with label=0.")
                return ""
            return " - " + "\n - ".join(bad_feedback)
        except Exception as e:
            self.logger.error(f"Error aggregating feedback: {e}")
            raise

    def generate_structured_feedback(self, task_description: str, feedback: str) -> str:
        """
        Generate structured feedback using the LLM.

        Args:
            task_description (str): Description of the evaluation task.
            feedback (str): Aggregated feedback for the task.

        Returns:
            str: Structured feedback generated by the LLM.
        """
        try:
            prompt_template = self.load_prompt("STRUCTURE_FEEDBACK.txt")
            formatted_prompt = prompt_template.format(
                task=task_description, feedback=feedback
            )
            structured_response = self.llm_engine.get_llm_completion(
                formatted_prompt, temperature=0.1
            )
            structured_feedback = structured_response.choices[0].message.content.strip()
            self.logger.info("Structured feedback generated successfully.")
            return structured_feedback
        except Exception as e:
            self.logger.error(f"Error generating structured feedback: {e}")
            raise

    def generate_rubric(
        self, dataset: Union[str, Path, List[Dict[str, Union[str, int]]]]
    ) -> None:
        """
        Executes the pipeline to generate a grading rubric and evaluate responses.

        Args:
            dataset (Union[str, Path, List[Dict[str, Union[str, int]]]]): Path to the dataset or a list of dictionaries.
        """
        try:
            self.data = self.load_data(dataset)
            aggregated_feedback = self.aggregate_feedback(self.data)
            if not aggregated_feedback:
                self.logger.warning("No feedback to process.")
                return

            task_description = (
                "Evaluate AI-generated responses based on their correctness and clarity. "
                "Assess responses as suitable (1) or unsuitable (0)."
            )
            structured_feedback = self.generate_structured_feedback(
                task_description, aggregated_feedback
            )
            rubric = self.generate_grading_notes(structured_feedback, task_description)

            self.logger.info("Rubric successfully generated.")
        except Exception as e:
            self.logger.error(f"Error during rubric generation: {e}")
            raise

    def judge(self, input: str, output: str = None) -> Judgment:
        """
        Judge a given input and output pair using the generated rubric.

        Args:
            input (str): Input query or task.
            output (str): AI-generated output to evaluate.

        Returns:
            Judgment: Contains the score and reasoning.
        """
        try:
            if not hasattr(self, "rubric") or not self.rubric:
                raise ValueError(
                    "Rubric not generated. Please run the pipeline first to generate the rubric."
                )

            user_prompt = dedent(
                f"""
                {self.rubric}
                Input: {input}
                Response: {output}
                Respond in JSON format: {{"REASONING": "[...]
                ", "SCORE": "<True/False>"}}.
                """
            )
            reasoning, score = self._judge(user_prompt=user_prompt, system_prompt=None)
            return Judgment(reasoning=reasoning, score=score)
        except Exception as e:
            self.logger.error(f"Error during judgment: {e}")
            raise
