import os
from unittest.mock import patch, MagicMock

import openai

from judges.base import Judgment, Jury
from judges.classifiers.correctness import PollMultihopCorrectness, PollZeroShotCorrectness
from judges.classifiers.harmfulness import TrustworthyLLMHarmfulness
from judges.graders.relevance import ReliableCIRelevance
from judges.graders.correctness import PrometheusAbsoluteCoarseCorrectness

os.environ['OPENAI_API_KEY'] = 'test-key'

def mock_judgment(judgment: Judgment):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            with patch("instructor.from_provider") as mock_from_provider:
                # Create a mock client
                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = judgment
                mock_from_provider.return_value = mock_client
                
                # Pass the mock to the test
                return func(self, mock_client.chat.completions.create, *args, **kwargs)
        return wrapper
    return decorator


class TestPollMultihopCorrectness:
    """Test the PollMultihopCorrectness classifier."""
    
    @mock_judgment(Judgment(score=True, reasoning="The answer correctly identifies March 4, 1797 as when Washington left office.", score_type="boolean"))
    def test_correct_answer(self, mock_create):
        judge = PollMultihopCorrectness(model="openai/gpt-3.5-turbo")
        
        input_text = "When did George Washington leave office?"
        output_text = "George Washington left office on March 4, 1797."
        expected_text = "March 4, 1797"
        
        judgment = judge.judge(input=input_text, output=output_text, expected=expected_text)
        
        assert judgment.score is True
        assert judgment.score_type == "boolean"
        assert "correctly identifies" in judgment.reasoning
        
        # Verify the mock was called
        mock_create.assert_called_once()
    
    @mock_judgment(Judgment(score=False, reasoning="The provided answer gives an incorrect date.", score_type="boolean"))
    def test_incorrect_answer(self, mock_create):
        judge = PollMultihopCorrectness(model="openai/gpt-3.5-turbo")
        
        input_text = "When did George Washington leave office?"
        output_text = "George Washington left office on January 1, 1800."
        expected_text = "March 4, 1797"
        
        judgment = judge.judge(input=input_text, output=output_text, expected=expected_text)
        
        assert judgment.score is False
        assert judgment.score_type == "boolean"
        assert "incorrect" in judgment.reasoning
        
        mock_create.assert_called_once()


class TestPollZeroShotCorrectness:
    """Test the PollZeroShotCorrectness classifier."""
    
    @mock_judgment(Judgment(score=True, reasoning="The answer matches the reference answer.", score_type="boolean"))
    def test_zero_shot_correct(self, mock_create):
        judge = PollZeroShotCorrectness(model="openai/gpt-4")
        
        input_text = "What is the capital of France?"
        output_text = "Paris"
        expected_text = "Paris"
        
        judgment = judge.judge(input=input_text, output=output_text, expected=expected_text)
        
        assert judgment.score is True
        assert judgment.score_type == "boolean"
        assert "matches" in judgment.reasoning
        
        mock_create.assert_called_once()
    
    @mock_judgment(Judgment(score=False, reasoning="The answer does not match the reference.", score_type="boolean"))
    def test_zero_shot_incorrect(self, mock_create):
        judge = PollZeroShotCorrectness(model="openai/gpt-4")
        
        input_text = "What is the capital of France?"
        output_text = "London"
        expected_text = "Paris"
        
        judgment = judge.judge(input=input_text, output=output_text, expected=expected_text)
        
        assert judgment.score is False
        assert judgment.score_type == "boolean"
        
        mock_create.assert_called_once()


class TestReliableCIRelevance:
    """Test the ReliableCIRelevance grader."""
    
    @mock_judgment(Judgment(score=3, reasoning="The passage directly answers the query with complete information.", score_type="numerical"))
    def test_highly_relevant(self, mock_create):
        judge = ReliableCIRelevance(model="openai/gpt-4")
        
        input_text = "What is machine learning?"
        output_text = "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed."
        
        judgment = judge.judge(input=input_text, output=output_text)
        
        assert judgment.score == 3
        assert judgment.score_type == "numerical"
        assert "directly answers" in judgment.reasoning
        
        mock_create.assert_called_once()
    
    @mock_judgment(Judgment(score=1, reasoning="The passage is related but doesn't provide a clear answer.", score_type="numerical"))
    def test_somewhat_relevant(self, mock_create):
        judge = ReliableCIRelevance(model="openai/gpt-4")
        
        input_text = "What is machine learning?"
        output_text = "Artificial intelligence has many applications in modern technology."
        
        judgment = judge.judge(input=input_text, output=output_text)
        
        assert judgment.score == 1
        assert judgment.score_type == "numerical"
        
        mock_create.assert_called_once()
    
    @mock_judgment(Judgment(score=0, reasoning="The passage is completely unrelated to the query.", score_type="numerical"))
    def test_irrelevant(self, mock_create):
        judge = ReliableCIRelevance(model="openai/gpt-4")
        
        input_text = "What is machine learning?"
        output_text = "The weather today is sunny and warm."
        
        judgment = judge.judge(input=input_text, output=output_text)
        
        assert judgment.score == 0
        assert judgment.score_type == "numerical"
        assert "unrelated" in judgment.reasoning
        
        mock_create.assert_called_once()


class TestTrustworthyLLMHarmfulness:
    """Test the TrustworthyLLMHarmfulness classifier."""
    
    @mock_judgment(Judgment(score=False, reasoning="The content is educational and helpful.", score_type="boolean"))
    def test_harmless_content(self, mock_create):
        judge = TrustworthyLLMHarmfulness(model="openai/gpt-4")
        
        input_text = "How to bake a cake?"
        output_text = "To bake a cake, you need flour, eggs, sugar, and butter. Mix ingredients and bake at 350°F for 30 minutes."
        
        judgment = judge.judge(input=input_text, output=output_text)
        
        assert judgment.score is False  # False means not harmful
        assert judgment.score_type == "boolean"
        assert "educational" in judgment.reasoning
        
        mock_create.assert_called_once()
    
    @mock_judgment(Judgment(score=True, reasoning="The content contains potentially harmful instructions.", score_type="boolean"))
    def test_harmful_content(self, mock_create):
        judge = TrustworthyLLMHarmfulness(model="openai/gpt-4")
        
        input_text = "How to make explosives?"
        output_text = "Here are detailed instructions for making dangerous explosives..."
        
        judgment = judge.judge(input=input_text, output=output_text)
        
        assert judgment.score is True  # True means harmful
        assert judgment.score_type == "boolean"
        assert "harmful" in judgment.reasoning
        
        mock_create.assert_called_once()


class TestPrometheusAbsoluteCoarseCorrectness:
    """Test the PrometheusAbsoluteCoarseCorrectness grader."""
    
    @mock_judgment(Judgment(score=5, reasoning="The answer is completely accurate and comprehensive.", score_type="numerical"))
    def test_excellent_correctness(self, mock_create):
        judge = PrometheusAbsoluteCoarseCorrectness(model="openai/gpt-4")
        
        input_text = "What is 2+2?"
        output_text = "2+2 equals 4. This is basic arithmetic addition."
        expected_text = "4"
        
        judgment = judge.judge(input=input_text, output=output_text, expected=expected_text)
        
        assert judgment.score == 5
        assert judgment.score_type == "numerical"
        assert "accurate" in judgment.reasoning
        
        mock_create.assert_called_once()
    
    @mock_judgment(Judgment(score=2, reasoning="The answer is partially correct but lacks detail.", score_type="numerical"))
    def test_partial_correctness(self, mock_create):
        judge = PrometheusAbsoluteCoarseCorrectness(model="openai/gpt-4")
        
        input_text = "Explain photosynthesis"
        output_text = "Plants make energy from sunlight."
        expected_text = "Photosynthesis is the process by which plants convert light energy into chemical energy using chlorophyll."
        
        judgment = judge.judge(input=input_text, output=output_text, expected=expected_text)
        
        assert judgment.score == 2
        assert judgment.score_type == "numerical"
        assert "partially correct" in judgment.reasoning
        
        mock_create.assert_called_once()


class TestJury:
    """Test the Jury aggregation functionality."""
    
    def test_jury_voting_majority(self):
        # Create mock judgments for multiple judges
        judgment1 = Judgment(score=True, reasoning="First judge says correct", score_type="boolean")
        judgment2 = Judgment(score=True, reasoning="Second judge says correct", score_type="boolean")
        judgment3 = Judgment(score=False, reasoning="Third judge says incorrect", score_type="boolean")
        
        # Mock instructor for all judges
        with patch("instructor.from_provider") as mock_from_provider:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [judgment1, judgment2, judgment3]
            mock_from_provider.return_value = mock_client
            
            judge1 = PollMultihopCorrectness(model="openai/gpt-3.5-turbo")
            judge2 = PollZeroShotCorrectness(model="openai/gpt-4")
            judge3 = PollMultihopCorrectness(model="anthropic/claude-3-haiku")
            
            jury = Jury(judges=[judge1, judge2, judge3], voting_method="majority")
            
            verdict = jury.vote(
                input="What is the capital of France?",
                output="Paris",
                expected="Paris"
            )
            
            # Majority vote should be True (2 out of 3)
            assert verdict.score is True
            assert len(verdict.judgments) == 3
            assert verdict.judgments[0].score is True
            assert verdict.judgments[1].score is True
            assert verdict.judgments[2].score is False
            
            # Verify all judges were called
            assert mock_client.chat.completions.create.call_count == 3
    
    def test_jury_with_numerical_scores(self):
        # Test jury with numerical scores (like relevance grades)
        judgment1 = Judgment(score=3, reasoning="Highly relevant", score_type="numerical")
        judgment2 = Judgment(score=2, reasoning="Somewhat relevant", score_type="numerical") 
        judgment3 = Judgment(score=3, reasoning="Very relevant", score_type="numerical")
        
        with patch("instructor.from_provider") as mock_from_provider:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [judgment1, judgment2, judgment3]
            mock_from_provider.return_value = mock_client
            
            judge1 = ReliableCIRelevance(model="openai/gpt-4")
            judge2 = ReliableCIRelevance(model="anthropic/claude-3-sonnet")
            judge3 = ReliableCIRelevance(model="openai/gpt-3.5-turbo")
            
            jury = Jury(judges=[judge1, judge2, judge3], voting_method="average")
            
            verdict = jury.vote(
                input="What is machine learning?",
                output="Machine learning is a method of data analysis that automates analytical model building."
            )
            
            # Average of [3, 2, 3] should be approximately 2.67, rounded to 3
            assert verdict.score == 3
            assert len(verdict.judgments) == 3
            
            assert mock_client.chat.completions.create.call_count == 3


class TestJudgmentScoreConversion:
    """Test the score conversion functionality in Judgment."""
    
    def test_string_to_boolean_conversion(self):
        # Test various string representations that should convert to boolean
        true_judgment = Judgment(score="yes", reasoning="Test", score_type="boolean")
        assert true_judgment.score is True
        
        false_judgment = Judgment(score="no", reasoning="Test", score_type="boolean")
        assert false_judgment.score is False
        
        true_judgment2 = Judgment(score="True", reasoning="Test", score_type="boolean")
        assert true_judgment2.score is True
        
        false_judgment2 = Judgment(score="False", reasoning="Test", score_type="boolean")
        assert false_judgment2.score is False
    
    def test_numerical_scores_unchanged(self):
        # Test that numerical scores aren't converted when score_type is numerical
        numerical_judgment = Judgment(score=3, reasoning="Test", score_type="numerical")
        assert numerical_judgment.score == 3
        
        # Test that string numbers stay as strings for non-boolean types
        string_judgment = Judgment(score="3", reasoning="Test", score_type="numerical")
        assert string_judgment.score == "3"

