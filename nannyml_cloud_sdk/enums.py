from typing import Literal


ProblemType = Literal[
    'BINARY_CLASSIFICATION',
    'MULTICLASS_CLASSIFICATION',
    'REGRESSION',
]

FeatureType = Literal['CONTINUOUS', 'CATEGORY']

ColumnType = Literal[
  'TARGET',
  'PREDICTION_SCORE',
  'PREDICTION',
  'TIMESTAMP',
  'CATEGORICAL_FEATURE',
  'CONTINUOUS_FEATURE',
  'IGNORED',
  'IDENTIFIER',
]
