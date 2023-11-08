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

ChunkPeriod = Literal[
    'YEARLY',
    'QUARTERLY',
    'MONTHLY',
    'WEEKLY',
    'DAILY',
    'HOURLY',
]

PerformanceMetric = Literal[
    'ROC_AUC',
    'F1',
    'PRECISION',
    'RECALL',
    'SPECIFICITY',
    'ACCURACY',
    'CONFUSION_MATRIX',
    'BUSINESS_VALUE',
    'MAE',
    'MAPE',
    'MSE',
    'RMSE',
    'MSLE',
    'RMSLE',
]

S3AuthenticationMode = Literal['ANONYMOUS', 'INTEGRATED', 'ACCESS_KEY']
