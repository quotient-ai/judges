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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class GradingNoteProcessor:
    """
    A class to process AI-generated responses, generate grading notes using an LLM,
    evaluate responses, and compute evaluation metrics.
    """

    def __init__(
            self,
            prompts_dir: Optional[str] = None,
            grading_notes_dir: Optional[str] = None,
            max_rows: Optional[int] = None,
            llm_engine: Optional[LLMRecommendationEngine] = None
    ):
        """
        Initializes the GradingNoteProcessor with necessary configurations.

        Args:
            prompts_dir (Optional[str]): Directory path where prompt templates are stored.
            grading_notes_dir (Optional[str]): Directory path to save generated grading notes.
            max_rows (Optional[int]): Maximum number of rows to process for testing.
            llm_engine (Optional[LLMRecommendationEngine]): Instance of LLMRecommendationEngine.
        """
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
        self.data: List[Dict[str, Union[str, int]]] = []
        self.grading_notes: str = ""

    def load_data(self, dataset: Union[str, Path, List[Dict[str, Union[str, int]]]]):
        """Loads the dataset from a CSV file or a JSON list into a list of dictionaries.

        Args:
            dataset (Union[str, Path, List[Dict[str, Union[str, int]]]]):
                - Path to the dataset CSV file.
                - List of dictionaries representing the dataset.
        """
        try:
            if isinstance(dataset, (str, Path)):
                dataset_path = Path(dataset)
                self.logger.info(f"Loading data from {dataset_path}")

                with dataset_path.open('r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    self.data = []
                    for idx, row in enumerate(reader):
                        if self.max_rows and idx >= self.max_rows:
                            break
                        self.data.append(row)

                self.logger.info(f"Data loaded successfully with {len(self.data)} records.")
            elif isinstance(dataset, list):
                self.logger.info(f"Loading data from JSON payload with {len(dataset)} records.")
                self.data = dataset[:self.max_rows] if self.max_rows else dataset
                self.logger.info(f"Data loaded successfully with {len(self.data)} records.")
            else:
                raise TypeError("Dataset must be a file path or a list of dictionaries.")
        except FileNotFoundError:
            self.logger.error(f"Data file not found at {dataset}")
            raise
        except csv.Error as e:
            self.logger.error(f"Error parsing CSV file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error loading data: {e}")
            raise

    def aggregate_feedback(self) -> str:
        """Aggregates feedback from bad data points into a single formatted string.

        Returns:
            str: Aggregated feedback string.
        """
        try:
            self.logger.info("Aggregating feedback from bad data points.")
            bad_data_points = [row for row in self.data if int(row.get('label', 0)) == 0]
            if not bad_data_points:
                self.logger.warning("No bad data points found with label=0.")
                return ""
            aggregated_feedback = ' - ' + '\n - '.join(
                row['feedback'] for row in bad_data_points if row.get('feedback')
            )
            self.logger.debug(f"Aggregated Feedback: {aggregated_feedback}")
            return aggregated_feedback
        except KeyError as e:
            self.logger.error(f"Missing expected column in data: {e}")
            raise
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
            str: Generated grading notes.
        """
        try:
            self.logger.info("Generating grading notes using LLM.")
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

            # Append formatting instructions
            grading_notes += "\n\n" + grading_note_format_instructions
            self.logger.debug(f"Generated Grading Notes: {grading_notes}")
            self.grading_notes = grading_notes
            return grading_notes
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
                    grading_note_formatted = self.grading_notes.format(input_text=input_text, completion=completion)
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

    def run_pipeline(self):
        """Executes the full processing pipeline."""
        try:
            # At this point, dataset should have been loaded via API
            if not self.data:
                self.logger.error("No data loaded. Cannot run pipeline.")
                raise ValueError("Dataset is empty.")

            aggregated_feedback = self.aggregate_feedback()
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
            self.save_grading_notes()

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

    # API Methods
    def generate_structured_feedback_api(self, task_description: str, dataset: Union[str, Path, List[Dict[str, Union[str, int]]]]) -> str:
        """
        API method to generate structured feedback based on task description and dataset.

        Args:
            task_description (str): Description of the task.
            dataset (Union[str, Path, List[Dict[str, Union[str, int]]]]): 
                - Path to the dataset CSV file or a list of dictionaries representing the dataset.

        Returns:
            str: Structured feedback.
        """
        try:
            # Load data
            self.load_data(dataset)

            # Aggregate feedback
            aggregated_feedback = self.aggregate_feedback()
            if not aggregated_feedback:
                self.logger.warning("No feedback to process.")
                return ""

            # Generate structured feedback
            structured_feedback = self.generate_structured_feedback(task_description, aggregated_feedback)
            return structured_feedback
        except Exception as e:
            self.logger.error(f"API Error in generate-rubric: {e}")
            raise

    def generate_grading_notes_api(self, task_description: str, structured_feedback: str) -> str:
        """
        API method to generate grading notes based on task description and structured feedback.

        Args:
            task_description (str): Description of the task.
            structured_feedback (str): Structured feedback.

        Returns:
            str: Generated grading notes.
        """
        try:
            # Generate grading notes
            grading_notes = self.generate_grading_notes(structured_feedback, task_description)
            return grading_notes
        except Exception as e:
            self.logger.error(f"API Error in generate_grading_notes: {e}")
            raise

    def generate_evaluation_api(self, dataset: Union[str, Path, List[Dict[str, Union[str, int]]]], grading_note: str) -> dict:
        """
        API method to evaluate responses and compute metrics.

        Args:
            dataset (Union[str, Path, List[Dict[str, Union[str, int]]]]):
                Path to the dataset CSV file or a list of dictionaries representing the dataset.
            grading_note (str): The grading note to be used for evaluating the dataset.

        Returns:
            dict: Evaluation metrics.
        """
        try:
            # Load the provided dataset (either from a file or as a JSON-like object)
            self.load_data(dataset)

            # Set the grading note provided in the argument
            self.grading_notes = grading_note

            # Evaluate responses using the provided grading note
            self.evaluate_responses_multithreaded()

            # Extract classifications from the evaluations
            self.extract_classifications()

            # Compute and return metrics
            metrics = self.compute_metrics()
            return metrics
        except ValueError as ve:
            self.logger.error(f"ValueError in generate_evaluation_api: {ve}")
            raise
        except KeyError as ke:
            self.logger.error(f"KeyError in generate_evaluation_api: {ke}")
            raise
        except Exception as e:
            self.logger.error(f"Error in generate_evaluation_api: {e}")
            raise
