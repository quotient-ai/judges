from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from tqdm import tqdm
from pathlib import Path
import logging
from typing import Optional, Union, List, Dict
from metrics.compute_metrics import ComputeMetrics
from engine.llm_engine import LLMRecommendationEngine, GradingNote
import os
import tempfile



from textwrap import dedent

from judges.base import BaseJudge, Judgment


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)



class AutoJudge(BaseJudge):
    """
    A class to process AI-generated responses, generate grading notes using an LLM,
    evaluate responses, and compute evaluation metrics.
    """

    def __init__(
            self,
            prompts_dir: Optional[str] = "./prompts",
            grading_notes_dir: Optional[str] = "/tmp/grading_notes",
            max_rows: Optional[int] = None,
            llm_engine: Optional[LLMRecommendationEngine] = None,
            model: str = "gpt-4o-mini"  # Add a default model name
    ):
        """
        Initializes the GradingNoteProcessor with necessary configurations.

        Args:
            prompts_dir (Optional[str]): Directory path where prompt templates are stored.
            grading_notes_dir (Optional[str]): Directory path to save generated grading notes.
            max_rows (Optional[int]): Maximum number of rows to process for testing.
            llm_engine (Optional[LLMRecommendationEngine]): Instance of LLMRecommendationEngine.
            model (str): Model name used for evaluation in BaseJudge.
        """
        super().__init__(model=model)  # Call BaseJudge's constructor

        self.logger = logging.getLogger(self.__class__.__name__)

        # Set the prompts directory; if not provided, use the default relative path
        if prompts_dir is None:
            self.prompts_dir = Path(os.path.join(os.path.dirname(__file__), '..', 'prompts')).resolve()
        else:
            self.prompts_dir = Path(prompts_dir).resolve()

        # Set the grading notes directory; default to /tmp/grading_notes
        if grading_notes_dir is None:
            self.grading_notes_dir = Path("/tmp/grading_notes")
        else:
            self.grading_notes_dir = Path(grading_notes_dir)

        # Create the grading notes directory if it doesn't exist
        self.grading_notes_dir.mkdir(parents=True, exist_ok=True)

        self.max_rows = max_rows

        # Initialize LLM engine
        self.llm_engine = llm_engine or LLMRecommendationEngine()

        # Initialize placeholders for data and grading notes
        self.grading_notes: str = ""


    def load_data(self, dataset: Union[str, Path, List[Dict[str, Union[str, int]]]]) -> List[Dict[str, Union[str, int]]]:
        """Loads the dataset from a CSV file or list of dictionaries and returns it."""
        self.logger.info("Loading dataset...")
        data = []
        try:
            if isinstance(dataset, (str, Path)):
                dataset_path = Path(dataset)
                with dataset_path.open('r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    data = [row for idx, row in enumerate(reader) if not self.max_rows or idx < self.max_rows]
            elif isinstance(dataset, list):
                data = dataset[:self.max_rows] if self.max_rows else dataset
            else:
                raise TypeError("Dataset must be a file path or a list of dictionaries.")
            self.logger.info(f"Data loaded successfully with {len(data)} records.")
            return data  # Return the loaded data
        except Exception as e:
            self.logger.error(f"Error loading dataset: {e}")
            raise


    def aggregate_feedback(self, data) -> str:
        """Aggregates feedback from bad data points into a single formatted string."""
        try:
            self.logger.info("Aggregating feedback from bad data points.")
            # Handle label as string or integer and ensure feedback exists
            bad_data_points = [
                row for row in data
                if str(row.get('label', "0")).strip() == "0" and row.get('feedback')
            ]
            if not bad_data_points:
                self.logger.warning("No bad data points found with label=0.")
                return ""

            aggregated_feedback = ' - ' + '\n - '.join(row['feedback'] for row in bad_data_points)
            self.logger.debug(f"Aggregated Feedback: {aggregated_feedback}")
            return aggregated_feedback
        except Exception as e:
            self.logger.error(f"Error aggregating feedback: {e}")
            raise



    def load_prompt(self, prompt_filename: str) -> str:
        """Loads a prompt template from the prompts directory.

        Args:
            prompt_filename (str): Filename of the prompt template.

        Returns:
            str: Content of the prompt template.
        """
        prompt_path = self.prompts_dir / prompt_filename
        try:
            self.logger.info(f"Loading prompt from {prompt_path}")
            with prompt_path.open('r', encoding='utf-8') as file:
                prompt_content = file.read()
            return prompt_content
        except FileNotFoundError:
            self.logger.error(f"Prompt file not found: {prompt_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading prompt {prompt_filename}: {e}")
            raise

    def generate_structured_feedback(self, task_description: str, feedback: str) -> str:
        """Generates structured feedback using the LLM.

        Args:
            task_description (str): Description of the task for the LLM.
            feedback (str): Aggregated feedback to be structured.

        Returns:
            str: Structured feedback generated by the LLM.
        """
        try:
            self.logger.info("Generating structured feedback using LLM.")
            structure_feedback_prompt = self.load_prompt('.//STRUCTURE_FEEDBACK.txt')
            formatted_prompt = structure_feedback_prompt.format(task=task_description, feedback=feedback)
            structured_feedback = self.llm_engine.get_llm_completion(
                formatted_prompt,
                temperature=0.1
            )
            structured_content = structured_feedback.choices[0].message.content.strip()
            self.logger.debug(f"Structured Feedback: {structured_content}")
            return structured_content
        except Exception as e:
            self.logger.error(f"Error generating structured feedback: {e}")
            raise

    def generate_grading_notes(self, structured_feedback: str, task_description: str) -> str:
        """Generates grading notes using the LLM based on structured feedback.

        Args:
            structured_feedback (str): Structured feedback from the LLM.
            task_description (str): Description of the task.

        Returns:
            str: Generated grading notes with formatting instructions.
        """
        try:
            self.logger.info("Generating grading notes using LLM.")
            generate_rubric_prompt = self.load_prompt('GENERATE_RUBRIC.txt')
            grading_note_format_instructions = self.load_prompt('RUBRIC_FORMAT.txt')

            # Format the prompt for the LLM
            formatted_prompt = generate_rubric_prompt.format(
                feedback=structured_feedback,
                task=task_description
            )

            # Generate the raw rubric
            rubric_response = self.llm_engine.get_llm_completion(
                formatted_prompt,
                temperature=0
            )
            raw_rubric = rubric_response.choices[0].message.content.strip()

            # Store raw rubric separately
            self.rubric = raw_rubric

            # Append formatting instructions
            formatted_rubric = f"{raw_rubric}\n\n{grading_note_format_instructions}"

            # Store formatted rubric for evaluation
            self.grading_notes = formatted_rubric

            self.logger.debug(f"Generated Rubric: {self.rubric}")
            self.logger.debug(f"Formatted Rubric: {self.grading_notes}")

            return self.grading_notes
        except Exception as e:
            self.logger.error(f"Error generating grading notes: {e}")
            raise


    def save_grading_notes(self, iteration: int = 1):
        """Saves the generated grading notes to a file.

        Args:
            iteration (int): Iteration number for the grading notes filename.
        """
        try:
            filename = f'grading_note_iteration_{iteration}.txt'
            grading_note_path = self.grading_notes_dir / filename
            self.logger.info(f"Saving grading notes to {grading_note_path}")
            with grading_note_path.open('w', encoding='utf-8') as file:
                file.write(self.grading_notes)
            self.logger.info("Grading notes saved successfully.")
        except Exception as e:
            self.logger.error(f"Error saving grading notes: {e}")
            raise

    def evaluate_responses_multithreaded(self, max_workers=5):
        """
        Evaluates each response in the dataset using multithreaded LLM completions.
        
        Args:
            max_workers (int): Maximum number of threads to use for parallel LLM completions.
        """
        if not self.grading_notes:
            self.logger.error("Grading notes not generated. Cannot evaluate responses.")
            raise ValueError("Grading notes are missing.")

        self.logger.info(f"Evaluating responses using generated grading notes with {max_workers} threads.")
        try:
            # Ensure 'completion' column exists
            if not self.data or 'completion' not in self.data[0]:
                self.logger.error("'completion' column not found in the dataset.")
                raise KeyError("'completion' column missing.")

            self.generated_grading_note_evals: List[GradingNote] = []

            # Helper function for handling individual LLM completions
            def process_single_response(row):
                completion = row.get('completion', '')
                input_text = row.get('input_text', '')
                if not completion:
                    self.logger.info("Empty completion found. Classification will be False")
                    return GradingNote(
                        Classification=False,
                        Explanation="No response provided for evaluation."
                    )
                try:
                    grading_note_formatted = self.grading_notes.format(input=input_text, output=completion)
                    grading_note = self.llm_engine.get_llm_completion(
                        grading_note_formatted,
                        model="gpt-4-turbo-2024-04-09",
                        response_model=GradingNote,
                        system_prompt=None,
                        temperature=0
                    )
                    return grading_note
                except Exception as e:
                    self.logger.error(f"Error processing completion: {e}")
                    return GradingNote(Classification=False, Explanation="LLM Error: Failed to generate response.")

            # Use ThreadPoolExecutor to parallelize the LLM completion calls
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_row = {executor.submit(process_single_response, row): row for row in self.data}
                for future in as_completed(future_to_row):
                    grading_note_result = future.result()
                    self.generated_grading_note_evals.append(grading_note_result)

            self.logger.info("Completed evaluating all responses.")
        except Exception as e:
            self.logger.error(f"Error during multithreaded response evaluation: {e}")
            raise

    def extract_classifications(self):
        """Extracts classification results from LLM evaluations."""
        self.logger.info("Extracting classification results from LLM evaluations.")
        try:
            self.generated_grading_note_classifications: List[int] = []
            for eval_result in self.generated_grading_note_evals:
                classification = 1 if getattr(eval_result, 'Classification', False) else 0
                self.generated_grading_note_classifications.append(classification)
            self.logger.debug("Classification extraction completed.")
        except Exception as e:
            self.logger.error(f"Error extracting classifications: {e}")
            raise

    def compute_metrics(self) -> dict:
        """Computes evaluation metrics comparing model predictions with human labels.

        Returns:
            dict: Dictionary containing Cohen's kappa, accuracy, precision, and recall.
        """
        self.logger.info("Computing evaluation metrics.")
        try:
            true_labels = [int(row['label']) for row in self.data]
            predicted_labels = self.generated_grading_note_classifications

            self.logger.info(f"true labels: {true_labels}")
            self.logger.info(f"predicted labels: {predicted_labels}")

            compute_metrics = ComputeMetrics(
                true_labels,
                predicted_labels
            )
            metrics = {
                'Cohen\'s kappa': compute_metrics.calculate_kappa(),
                'Accuracy': compute_metrics.calculate_accuracy(),
                'Precision': compute_metrics.calculate_precision(),
                'Recall': compute_metrics.calculate_recall(),
                'F1 Score': compute_metrics.calculate_f1()
            }
            self.logger.info(f"Computed Metrics: {metrics}")
            return metrics
        except Exception as e:
            self.logger.error(f"Error computing metrics: {e}")
            raise

    def generate_rubric(self, dataset: Union[str, Path, List[Dict[str, Union[str, int]]]]):
        """Executes the full processing pipeline."""

        self.data = self.load_data(dataset)

        try:
            # At this point, dataset should have been loaded via API
            if not self.data:
                self.logger.error("No data loaded. Cannot run pipeline.")
                raise ValueError("Dataset is empty.")

            aggregated_feedback = self.aggregate_feedback(self.data)
            if not aggregated_feedback:
                self.logger.warning("No feedback to process. Exiting pipeline.")
                return

            task_description = (
                "The task involves assessing the quality of AI-generated responses by evaluating whether "
                "each completion (the assistant’s reply) appropriately and effectively addresses the "
                "corresponding input_text (the user’s query), with labels indicating whether the response "
                "is suitable (1) or unsuitable (0)."
            )

            structured_feedback = self.generate_structured_feedback(task_description, aggregated_feedback)
            grading_notes = self.generate_grading_notes(structured_feedback, task_description)

            self.evaluate_responses_multithreaded()
            self.extract_classifications()
            metrics = self.compute_metrics()

            # Display sample outputs
            self.logger.info("Sample LLM Outputs:")
            for eval_result in self.generated_grading_note_evals[:5]:
                self.logger.info(eval_result)

            self.logger.info("Sample Classification Results (grading note):")
            classifications = {}
            for cls in self.generated_grading_note_classifications:
                classifications[cls] = classifications.get(cls, 0) + 1
            self.logger.info(classifications)

            self.logger.info("Sample Classification Results (human labels):")
            human_labels = {}
            for row in self.data[:10]:
                label = int(row['label'])
                human_labels[label] = human_labels.get(label, 0) + 1
            self.logger.info(human_labels)

            self.logger.info("Final Evaluation Metrics:")
            for metric, value in metrics.items():
                self.logger.info(f"{metric}: {value}")

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            raise

    

    # ================== JUDGE ==================

    def judge(
        self,
        input: str,
        output: str = None,
    ) -> Judgment:
        """
        Judge the input and return a verdict.
        """
        if not hasattr(self, "rubric") or not self.rubric:
            raise ValueError("Rubric not generated. Please run the pipeline first to generate the rubric.")
        
        system_prompt = None
        user_prompt = dedent(
            self.rubric +

            f"""
            
            Input: {input}
            Response: {output} 

            """
        )

        user_prompt += (
        'Respond in JSON format. {"REASONING": "[...]", "SCORE": "<your-score>"}'
        )

        reasoning, score = self._judge(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )
        return Judgment(reasoning=reasoning, score=score)