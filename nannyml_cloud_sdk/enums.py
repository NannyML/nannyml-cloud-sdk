from typing import Literal


ProductType = Literal[
    'MONITORING',
    'EVALUATION',
    'EXPERIMENT',
]
"""Product modules of NannyML Cloud"""


ProblemType = Literal[
    'BINARY_CLASSIFICATION',
    'MULTICLASS_CLASSIFICATION',
    'REGRESSION',
]
"""Problem types supported by NannyML Cloud."""


FeatureType = Literal['CONTINUOUS', 'CATEGORY']
"""Feature types supported by NannyML Cloud."""

ColumnType = Literal[
    'TARGET',
    'PREDICTION_SCORE',
    'PREDICTION',
    'TIMESTAMP',
    'CATEGORICAL_FEATURE',
    'CONTINUOUS_FEATURE',
    'IGNORED',
    'IDENTIFIER',
    'METRIC_NAME',
    'GROUP_NAME',
    'SUCCESS_COUNT',
    'FAIL_COUNT',
]
"""Schema column types defined by NannyML Cloud."""

ChunkPeriod = Literal[
    'YEARLY',
    'QUARTERLY',
    'MONTHLY',
    'WEEKLY',
    'DAILY',
    'HOURLY',
]
"""Time periods for chunking supported by NannyML Cloud."""

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
"""Performance metrics supported by NannyML Cloud."""

S3AuthenticationMode = Literal['ANONYMOUS', 'INTEGRATED', 'ACCESS_KEY']
"""Authentication modes for S3 access supported by NannyML Cloud.

- `ANONYMOUS`: No authentication required.
- `INTEGRATED`: Use the service account permissions the NannyML Cloud server has to access S3.
- `ACCESS_KEY`: Provide access key ID and secret to access S3.
"""

RunState = Literal['SCHEDULED', 'RUNNING', 'CANCELLING', 'COMPLETED']
"""States a NannyML run can be in.

- `SCHEDULED`: The run is scheduled to start at a later time.
- `RUNNING`: The run is currently active.
- `CANCELLING`: The run is currently being cancelled.
- `COMPLETED`: The run has completed (successfully or unsuccessfully).
"""

DataSourceEventType = Literal['CREATED', 'DATA_ADDED', 'DATA_REMOVED', 'DATA_UPDATED']
"""Events recorded for model data sources."""
