from typing import Literal

Chunking = Literal[
    'YEARLY',
    'QUARTERLY',
    'MONTHLY',
    'WEEKLY',
    'DAILY',
    'HOURLY',
    'NUMBER_OF_ROWS'
]

PerformanceType = Literal[
    'CBPE',
    'MCBPE',
    'DLE',
    'REALIZED'
]

UnivariateDriftMethod = Literal[
    'KOLMOGOROV_SMIRNOV',
    'JENSEN_SHANNON',
    'WASSERSTEIN',
    'HELLINGER',
    'L_INFINITY',
    'CHI2',
]

MultivariateDriftMethod = Literal[
    'PCA_RECONSTRUCTION_ERROR',
    'DOMAIN_CLASSIFIER_AUROC'
]

DataQualityMetric = Literal[
    'MISSING_VALUES',
    'UNSEEN_VALUES',
]

ConceptShiftMetric = Literal[
    'ROC_AUC',
    'F1',
    'AVERAGE_PRECISION',
    'PRECISION',
    'RECALL',
    'SPECIFICITY',
    'ACCURACY',
    'MAGNITUDE',
]

SummaryStatsMetric = Literal[
    'ROWS_COUNT',
    'SUMMARY_STATS_AVG',
    'SUMMARY_STATS_MEDIAN',
    'SUMMARY_STATS_STD',
    'SUMMARY_STATS_SUM',
]

ClassificationRuleType = Literal[
    'ANY',
    'EQUALS',
    'NOT_EQUALS',
    'CLASS',
]
