from statistics import median, mode
from typing import List, Union, Any

def _normalize_score(score: Any, score_type: str) -> float:
    """Normalize a score to a float value for voting."""
    if score_type == "boolean":
        if isinstance(score, str):
            if score.lower() in ["yes", "true", "1", "good"]:
                return 1.0
            elif score.lower() in ["no", "false", "0", "bad"]:
                return 0.0
        return float(score)
    elif score_type == "numerical":
        return float(score)
    elif score_type == "likert":
        # Map Likert scale to numerical values
        likert_map = {
            "terrible": 1.0,
            "bad": 2.0,
            "average": 3.0,
            "good": 4.0,
            "excellent": 5.0
        }
        return likert_map.get(str(score).lower(), 3.0)  # Default to average if unknown
    return float(score)  # Default to float conversion

def average_voting(scores: List[Any], score_types: List[str]) -> Union[float, bool]:
    """Calculate average vote, preserving boolean type if all scores are boolean."""
    if all(t == "boolean" for t in score_types):
        normalized_scores = [_normalize_score(s, t) for s, t in zip(scores, score_types)]
        avg = sum(normalized_scores) / len(normalized_scores) if normalized_scores else 0.0
        return avg > 0.5  # Convert back to boolean
    else:
        normalized_scores = [_normalize_score(s, t) for s, t in zip(scores, score_types)]
        return sum(normalized_scores) / len(normalized_scores) if normalized_scores else 0.0

def median_voting(scores: List[Any], score_types: List[str]) -> Union[float, bool]:
    """Calculate median vote, preserving boolean type if all scores are boolean."""
    if all(t == "boolean" for t in score_types):
        normalized_scores = [_normalize_score(s, t) for s, t in zip(scores, score_types)]
        med = median(normalized_scores) if normalized_scores else 0.0
        return med > 0.5  # Convert back to boolean
    else:
        normalized_scores = [_normalize_score(s, t) for s, t in zip(scores, score_types)]
        return median(normalized_scores) if normalized_scores else 0.0

def majority_voting(scores: List[Any], score_types: List[str]) -> Union[float, bool]:
    """Calculate majority vote, preserving boolean type if all scores are boolean."""
    if all(t == "boolean" for t in score_types):
        normalized_scores = [_normalize_score(s, t) for s, t in zip(scores, score_types)]
        try:
            vote = mode(normalized_scores)
        except:
            # If there's no unique mode, return the average as a fallback
            vote = sum(normalized_scores) / len(normalized_scores) if normalized_scores else 0.0
        return vote > 0.5  # Convert back to boolean
    else:
        normalized_scores = [_normalize_score(s, t) for s, t in zip(scores, score_types)]
        try:
            return mode(normalized_scores)
        except:
            return sum(normalized_scores) / len(normalized_scores) if normalized_scores else 0.0

def weighted_average_voting(scores: List[Any], weights: List[float], score_types: List[str]) -> Union[float, bool]:
    """Calculate weighted average vote, preserving boolean type if all scores are boolean."""
    if len(scores) != len(weights) or len(scores) != len(score_types):
        raise ValueError("scores, weights, and score_types must have the same length.")
    
    if all(t == "boolean" for t in score_types):
        normalized_scores = [_normalize_score(s, t) for s, t in zip(scores, score_types)]
        weighted_sum = sum(score * weight for score, weight in zip(normalized_scores, weights))
        total_weight = sum(weights)
        vote = weighted_sum / total_weight if total_weight != 0 else 0.0
        return vote > 0.5  # Convert back to boolean
    else:
        normalized_scores = [_normalize_score(s, t) for s, t in zip(scores, score_types)]
        weighted_sum = sum(score * weight for score, weight in zip(normalized_scores, weights))
        total_weight = sum(weights)
        return weighted_sum / total_weight if total_weight != 0 else 0.0

AVAILABLE_VOTING_METHODS = {
    "average": average_voting,
    "median": median_voting,
    "majority": majority_voting,
    "weighted_average": weighted_average_voting,
}