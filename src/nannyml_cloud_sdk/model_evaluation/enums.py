from typing import Literal

HypothesisType = Literal[
    'MODEL_PERFORMANCE_NO_WORSE_THAN_REFERENCE',
    'MODEL_PERFORMANCE_WITHIN_RANGE',
]
"""Model evaluation hypotheses supported by NannyML Cloud."""
