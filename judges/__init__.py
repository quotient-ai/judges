from judges.base import Jury
from judges.classifiers import *
from judges.graders import *
from judges.classifiers.correctness import (
    PollKiltHotpotCorrectness, PollKiltNQCorrectness,
    PollMultihopCorrectness, PollZeroShotCorrectness, RAFTCorrectness
)
from judges.classifiers.hallucination import (
    HaluEvalAnswerNonFactual, HaluEvalDialogueResponseNonFactual, HaluEvalDocumentSummaryNonFactual
)
from judges.classifiers.harmfulness import TrustworthyLLMHarmfulness
from judges.classifiers.query_quality import FactAlignQueryQuality
from judges.classifiers.refusal import TrustworthyLLMRefusal

from judges.graders.correctness import PrometheusAbsoluteCoarseCorrectness
from judges.graders.empathy import (
    EmotionQueenImplicitEmotionRecognition, EmotionQueenIntentionRecognition,
    EmotionQueenKeyEventRecognition, EmotionQueenMixedEventRecognition
)
from judges.graders.information_coverage import HaystackBulletPointCoverageCorrectness
from judges.graders.moderator import ORBenchUserInputModeration, ORBenchUserOutputModeration
from judges.graders.query_quality import MagpieQueryQuality
from judges.graders.relevance import ReliableCIRelevance
from judges.graders.response_quality import MTBenchChatBotResponseQuality
from judges.graders.refusal_detection import ORBenchRefusalDetection
import enum

class choices_judges(enum.Enum):
    # Factual Correctness
    CorrectnessPollKiltHotpot = "PollKiltHotpotCorrectness"
    CorrectnessPollKiltNQ = "PollKiltNQCorrectness"
    CorrectnessPollMultihop = "PollMultihopCorrectness"
    CorrectnessPollZeroShot = "PollZeroShotCorrectness"
    CorrectnessRAFT = "RAFTCorrectness"

    # Hallucination
    HallucinationHaluEvalAnswerNonFactual = "HaluEvalAnswerNonFactual"
    HallucinationHaluEvalDialogueResponseNonFactual = "HaluEvalDialogueResponseNonFactual"
    HallucinationHaluEvalDocumentSummaryNonFactual = "HaluEvalDocumentSummaryNonFactual"

    # Harmfulness
    HarmfulnessTrustworthyLLMHarmfulness = "TrustworthyLLMHarmfulness"

    # Query Quality Evaluation
    FactAlignQueryQuality = "FactAlignQueryQuality"

    # Refusal
    RefusalTrustworthyLLMRefusal = "TrustworthyLLMRefusal"

    # Correctness graders
    PrometheusAbsoluteCoarseCorrectness = "PrometheusAbsoluteCoarseCorrectness"

    # Empathy graders
    EmotionQueenImplicitEmotionRecognition = "EmotionQueenImplicitEmotionRecognition"
    EmotionQueenIntentionRecognition = "EmotionQueenIntentionRecognition"
    EmotionQueenKeyEventRecognition = "EmotionQueenKeyEventRecognition"
    EmotionQueenMixedEventRecognition = "EmotionQueenMixedEventRecognition"

    # Information coverage graders
    HaystackBulletPointCoverage = "HaystackBulletPointCoverageCorrectness"

    # Moderation graders
    ORBenchUserInputModeration = "ORBenchUserInputModeration"
    ORBenchUserOutputModeration = "ORBenchUserOutputModeration"

    # Query quality graders
    MagpieQueryQuality = "MagpieQueryQuality"

    # Relevance graders
    ReliableCIRelevance = "ReliableCIRelevance"

    # Response quality graders
    MTBenchChatBotResponseQuality = "MTBenchChatBotResponseQuality"

    # Refusal detection graders
    ORBenchRefusalDetection = "ORBenchRefusalDetection"


JUDGE_MAPPING = {
    choices_judges.CorrectnessPollKiltHotpot: PollKiltHotpotCorrectness,
    choices_judges.CorrectnessPollKiltNQ: PollKiltNQCorrectness,
    choices_judges.CorrectnessPollMultihop: PollMultihopCorrectness,
    choices_judges.CorrectnessPollZeroShot: PollZeroShotCorrectness,
    choices_judges.CorrectnessRAFT: RAFTCorrectness,

    choices_judges.HallucinationHaluEvalAnswerNonFactual: HaluEvalAnswerNonFactual,
    choices_judges.HallucinationHaluEvalDialogueResponseNonFactual: HaluEvalDialogueResponseNonFactual,
    choices_judges.HallucinationHaluEvalDocumentSummaryNonFactual: HaluEvalDocumentSummaryNonFactual,

    choices_judges.HarmfulnessTrustworthyLLMHarmfulness: TrustworthyLLMHarmfulness,
    choices_judges.FactAlignQueryQuality: FactAlignQueryQuality,
    choices_judges.RefusalTrustworthyLLMRefusal: TrustworthyLLMRefusal,

    choices_judges.PrometheusAbsoluteCoarseCorrectness: PrometheusAbsoluteCoarseCorrectness,
    choices_judges.EmotionQueenImplicitEmotionRecognition: EmotionQueenImplicitEmotionRecognition,
    choices_judges.EmotionQueenIntentionRecognition: EmotionQueenIntentionRecognition,
    choices_judges.EmotionQueenKeyEventRecognition: EmotionQueenKeyEventRecognition,
    choices_judges.EmotionQueenMixedEventRecognition: EmotionQueenMixedEventRecognition,

    choices_judges.HaystackBulletPointCoverage: HaystackBulletPointCoverageCorrectness,
    choices_judges.ORBenchUserInputModeration: ORBenchUserInputModeration,
    choices_judges.ORBenchUserOutputModeration: ORBenchUserOutputModeration,

    choices_judges.MagpieQueryQuality: MagpieQueryQuality,
    choices_judges.ReliableCIRelevance: ReliableCIRelevance,
    choices_judges.MTBenchChatBotResponseQuality: MTBenchChatBotResponseQuality,
    choices_judges.ORBenchRefusalDetection: ORBenchRefusalDetection,
}

def get_judge_by_name(name: choices_judges):
    return JUDGE_MAPPING[name]

__all__ = ["Jury", "choices_judges", "get_judge_by_name"]

