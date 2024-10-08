from typing import Any, Dict, List, Optional, Union

from gql import gql

from .custom_metric import CustomMetricSummary, _CUSTOM_METRIC_SUMMARY_FRAGMENT
from .enums import (
    Chunking, ClassificationRuleType, PerformanceType, UnivariateDriftMethod, MultivariateDriftMethod,
    DataQualityMetric, ConceptShiftMetric, SummaryStatsMetric
)
from .schema import ModelSchema
from .._typing import GraphQLObject, TypedDict, is_gql_type
from ..client import execute
from ..enums import ProblemType, PerformanceMetric


class SupportConfig(TypedDict):
    """Utility class"""
    enabled: bool
    is_supported: bool
    support_reason: Optional[str]


class ChunkingConfiguration(TypedDict):
    """Chunking configuration"""
    chunking: Chunking
    number_of_rows: Optional[int]
    enabled: bool


class PerformanceTypesConfiguration(TypedDict):
    enabled: bool
    type_: PerformanceType


class PerformanceMetricsConfiguration(GraphQLObject):
    lowerValueLimit: Optional[float]
    upperValueLimit: Optional[float]
    threshold: Dict[str, Any]
    segmentThresholds: List
    metric: PerformanceMetric
    estimated: SupportConfig
    realized: SupportConfig


class BusinessValueRuleConfig(TypedDict):
    trueClass: ClassificationRuleType
    trueClassName: Optional[str]
    predictedClass: ClassificationRuleType
    predictedClassName: Optional[str]
    weight: float
    isDefaultRule: bool


class BusinessValueMetricConfig(PerformanceMetricsConfiguration):
    truePositiveWeight: float
    falsePositiveWeight: float
    trueNegativeWeight: float
    falseNegativeWeight: float
    rules: list[BusinessValueRuleConfig]


class UnivariateDriftConfiguration(GraphQLObject):
    """Univariate drift configuration"""
    lowerValueLimit: Optional[float]
    upperValueLimit: Optional[float]
    threshold: Dict[str, Any]
    segmentThresholds: List
    categorical: SupportConfig
    continuous: SupportConfig
    targets: SupportConfig
    predictions: SupportConfig
    predictedProbabilities: SupportConfig
    method: UnivariateDriftMethod


class MultivariateDriftConfiguration(GraphQLObject):
    lowerValueLimit: Optional[float]
    upperValueLimit: Optional[float]
    threshold: Dict[str, Any]
    segmentThresholds: List
    enabled: bool
    is_supported: bool
    support_reason: Optional[str]
    method: MultivariateDriftMethod


class DataQualityMetricConfiguration(GraphQLObject):
    lowerValueLimit: Optional[float]
    upperValueLimit: Optional[float]
    threshold: Dict[str, Any]
    segmentThresholds: List
    categorical: SupportConfig
    continuous: SupportConfig
    targets: SupportConfig
    predictions: SupportConfig
    predictedProbabilities: SupportConfig
    metric: DataQualityMetric
    normalize: bool


class ConceptShiftMetricConfiguration(GraphQLObject):
    lowerValueLimit: Optional[float]
    upperValueLimit: Optional[float]
    threshold: Dict[str, Any]
    segmentThresholds: List
    enabled: bool
    is_supported: bool
    support_reason: Optional[str]
    metric: ConceptShiftMetric


class SummaryStatsMetricConfiguration(GraphQLObject):
    lowerValueLimit: Optional[float]
    upperValueLimit: Optional[float]
    threshold: Dict[str, Any]
    segmentThresholds: List
    metric: SummaryStatsMetric


class SummaryStatsSimpleMetricConfig(SummaryStatsMetricConfiguration):
    enabled: bool
    is_supported: bool
    support_reason: Optional[str]


class SummaryStatsColumnMetricConfig(SummaryStatsMetricConfiguration):
    categorical: SupportConfig
    continuous: SupportConfig
    targets: SupportConfig
    predictions: SupportConfig
    predictedProbabilities: SupportConfig


class CustomMetricConfig(GraphQLObject):
    metric: CustomMetricSummary
    estimated: SupportConfig
    realized: SupportConfig
    threshold: Dict[str, Any]
    segmentThresholds: List


_THRESHOLD_FRAGMENT = """
    fragment MetricThresholdConfig on MetricConfig {
        __typename
        threshold {
          ...ThresholdDetails
        }
        segmentThresholds {
            segment {
                id
            }
            threshold {
                ...ThresholdDetails
            }
        }
    }
"""

_THRESHOLD_DETAILS_FRAGMENT = """
    fragment ThresholdDetails on Threshold {
        __typename
        ... on ConstantThreshold {
          lower
          upper
        }
        ... on StandardDeviationThreshold {
          stdLowerMultiplier
          stdUpperMultiplier
        }
    }
"""


_GET_DEFAULT_RUNTIME_CONFIGURATION = gql("""
    query getDefaultMonitoringRuntimeConfiguration($input: GetDefaultMonitoringRuntimeConfigInput!) {
        get_default_monitoring_runtime_config(input: $input) {
            dataChunking { chunking, enabled, nrOfRows }
            performanceTypes { enabled, isSupported, supportReason, type }
            performanceMetrics {
              lowerValueLimit
              upperValueLimit
              ...MetricThresholdConfig
              metric
              estimated { enabled, isSupported, supportReason }
              realized { enabled, isSupported, supportReason }
              ... on BusinessValueMetricConfig {
                truePositiveWeight
                falsePositiveWeight
                trueNegativeWeight
                falseNegativeWeight
                rules {
                    trueClass
                    trueClassName
                    predictedClass
                    predictedClassName
                    weight
                    isDefaultRule
                }
              }
              __typename
            }
            univariateDriftMethods {
              lowerValueLimit
              upperValueLimit
              ...MetricThresholdConfig
              categorical { enabled, isSupported, supportReason }
              continuous { enabled, isSupported, supportReason }
              targets { enabled, isSupported, supportReason }
              predictions { enabled, isSupported, supportReason }
              predictedProbabilities { enabled, isSupported, supportReason }
              method
              __typename
            }
            multivariateDriftMethods {
              lowerValueLimit
              upperValueLimit
              ...MetricThresholdConfig
              enabled
              isSupported
              supportReason
              method
              __typename
            }
            dataQualityMetrics {
              lowerValueLimit
              upperValueLimit
              ...MetricThresholdConfig
              categorical { enabled, isSupported, supportReason }
              continuous { enabled, isSupported, supportReason }
              targets { enabled, isSupported, supportReason }
              predictions { enabled, isSupported, supportReason }
              predictedProbabilities { enabled, isSupported, supportReason }
              metric
              normalize
              __typename
            }
            conceptShiftMetrics {
              lowerValueLimit
              upperValueLimit
              ...MetricThresholdConfig
              enabled
              isSupported
              supportReason
              metric
              __typename
            }
            summaryStatsMetrics {
              lowerValueLimit
              upperValueLimit
              ...MetricThresholdConfig
              ... on SummaryStatsSimpleMetricConfig {
                enabled
              }
              ... on SummaryStatsColumnMetricConfig {
                categorical {
                  enabled
                }
                continuous {
                  enabled
                }
                targets {
                  enabled
                }
                predictions {
                  enabled
                }
                predictedProbabilities {
                  enabled
                }
              }
              metric
              __typename
            }
            customMetrics {
                ...MetricThresholdConfig
                metric {
                    ...MetricSummary
                }
                estimated {
                    enabled
                }
                realized {
                    enabled
                }
            }
        }
    }
""" + _THRESHOLD_FRAGMENT + _THRESHOLD_DETAILS_FRAGMENT + _CUSTOM_METRIC_SUMMARY_FRAGMENT)


class RuntimeConfigurationDict(TypedDict):
    dataChunking: List[ChunkingConfiguration]
    performanceTypes: List[PerformanceTypesConfiguration]
    performanceMetrics: List[PerformanceMetricsConfiguration]
    univariateDriftMethods: List[UnivariateDriftConfiguration]
    multivariateDriftMethods: List[MultivariateDriftConfiguration]
    dataQualityMetrics: List[DataQualityMetricConfiguration]
    conceptShiftMetrics: List[ConceptShiftMetricConfiguration]
    summaryStatsMetrics: List[Union[SummaryStatsSimpleMetricConfig, SummaryStatsColumnMetricConfig]]
    customMetrics: list[CustomMetricConfig]


class RuntimeConfiguration:
    """Configuration of a monitoring model"""

    @staticmethod
    def default(
        problem_type: ProblemType,
        chunking: Chunking,
        schema: ModelSchema,
        has_analysis_targets: bool,
        nr_of_rows: Optional[int] = None
    ) -> dict[str, Any]:
        rc = execute(_GET_DEFAULT_RUNTIME_CONFIGURATION, {
            'input': {
                'problemType': problem_type,
                'chunking': chunking,
                'nrOfRows': nr_of_rows,
                'schema': {
                    'columns': [{
                        'name': column['name'],
                        'columnType': column['columnType']
                    } for column in schema['columns']],
                    'hasAnalysisTargets': has_analysis_targets,
                },
            }
        })['get_default_monitoring_runtime_config']
        return _to_input(rc)


def _to_input(rc: RuntimeConfigurationDict) -> dict[str, Any]:
    """Converts the (default) runtime configuration dict to the input format for the 'create' mutation"""

    return {
        'dataChunking': rc['dataChunking'],
        'performanceTypes': rc['performanceTypes'],
        'performanceMetrics': [_convert_performance_metric(m) for m in rc['performanceMetrics']],
        'univariateDriftMethods': [_convert_univariate_drift_method(m) for m in rc['univariateDriftMethods']],
        'multivariateDriftMethods': [
            _convert_multivariate_drift_method(m) for m in rc['multivariateDriftMethods']],
        'dataQualityMetrics': [_convert_data_quality_metric(m) for m in rc['dataQualityMetrics']],
        'conceptShiftMetrics': [_convert_concept_drift_metric(m) for m in rc['conceptShiftMetrics']],
        'summaryStatsMetrics': [_convert_summary_stats_metric(m) for m in rc['summaryStatsMetrics']],
        'customMetrics': [_convert_custom_metric(m) for m in rc['customMetrics']],
    }


def _convert_supports_config(s: SupportConfig) -> bool:
    if 'enabled' in s:
        return s['enabled']
    else:
        return False


def _convert_threshold(t: Optional[Dict[str, Any]]) -> Optional[dict[str, Any]]:
    if t is None:
        return None
    elif t['__typename'] == 'ConstantThreshold':
        return {
            'constant': {
                'lower': t['lower'],
                'upper': t['upper'],
            }
        }
    else:
        return {
            'standardDeviation': {
                'stdLowerMultiplier': t['stdLowerMultiplier'],
                'stdUpperMultiplier': t['stdUpperMultiplier'],
            }
        }


def _convert_segment_threshold(st: dict) -> dict:
    return {
        'segmentId': st['segment']['id'],
        'threshold': _convert_threshold(st['threshold'])
    }


def _convert_performance_metric(m: PerformanceMetricsConfiguration | BusinessValueMetricConfig) -> dict:
    return {
        'metric': m['metric'],
        'enabledEstimated': _convert_supports_config(m['estimated']),
        'enabledRealized': _convert_supports_config(m['realized']),
        'businessValue': None if not is_gql_type(m, BusinessValueMetricConfig) else {
            'truePositiveWeight': m['truePositiveWeight'],
            'falsePositiveWeight': m['falsePositiveWeight'],
            'trueNegativeWeight': m['trueNegativeWeight'],
            'falseNegativeWeight': m['falseNegativeWeight'],
            'rules': [{
                    'trueClass': rule['trueClass'],
                    'trueClassName': rule['trueClassName'],
                    'predictedClass': rule['predictedClass'],
                    'predictedClassName': rule['predictedClassName'],
                    'weight': rule['weight'],
                    'isDefaultRule': rule['isDefaultRule'],
                } for rule in m['rules']
            ],
        },
        'threshold': _convert_threshold(m['threshold']),
        'segmentThresholds': [_convert_segment_threshold(st) for st in m['segmentThresholds']],
    }


def _convert_univariate_drift_method(m: UnivariateDriftConfiguration) -> dict:
    return {
        'method': m['method'],
        'enabledCategorical': _convert_supports_config(m['categorical']),
        'enabledContinuous': _convert_supports_config(m['continuous']),
        'enabledTargets': _convert_supports_config(m['targets']),
        'enabledPredictions': _convert_supports_config(m['predictions']),
        'enabledPredictedProbabilities': _convert_supports_config(m['predictedProbabilities']),
        'threshold': _convert_threshold(m['threshold']),
        'segmentThresholds': [_convert_segment_threshold(st) for st in m['segmentThresholds']],
    }


def _convert_multivariate_drift_method(m: MultivariateDriftConfiguration) -> dict:
    return {
        'method': m['method'],
        'enabled': m['enabled'],
        'threshold': _convert_threshold(m['threshold']),
        'segmentThresholds': [_convert_segment_threshold(st) for st in m['segmentThresholds']],
    }


def _convert_data_quality_metric(m: DataQualityMetricConfiguration) -> dict:
    return {
        'metric': m['metric'],
        'normalize': m['normalize'],
        'enabledCategorical': _convert_supports_config(m['categorical']),
        'enabledContinuous': _convert_supports_config(m['continuous']),
        'enabledTargets': _convert_supports_config(m['targets']),
        'enabledPredictions': _convert_supports_config(m['predictions']),
        'enabledPredictedProbabilities': _convert_supports_config(m['predictedProbabilities']),
        'threshold': _convert_threshold(m['threshold']),
        'segmentThresholds': [_convert_segment_threshold(st) for st in m['segmentThresholds']],
    }


def _convert_concept_drift_metric(m: ConceptShiftMetricConfiguration) -> dict:
    return {
        'metric': m['metric'],
        'enabled': m['enabled'],
        'threshold': _convert_threshold(m['threshold']),
        'segmentThresholds': [_convert_segment_threshold(st) for st in m['segmentThresholds']],
    }


def _convert_summary_stats_metric(m: SummaryStatsMetricConfiguration) -> dict:
    res: dict[str, Any] = {
        'metric': m['metric'],
        'threshold': _convert_threshold(m['threshold']),
        'segmentThresholds': [_convert_segment_threshold(st) for st in m['segmentThresholds']],
    }
    if is_gql_type(m, SummaryStatsSimpleMetricConfig):
        res['enabled'] = m['enabled']
    elif is_gql_type(m, SummaryStatsColumnMetricConfig):
        res['metric'] = m['metric']
        res['enabledCategorical'] = _convert_supports_config(m['categorical'])
        res['enabledContinuous'] = _convert_supports_config(m['continuous'])
        res['enabledTargets'] = _convert_supports_config(m['targets'])
        res['enabledPredictions'] = _convert_supports_config(m['predictions'])
        res['enabledPredictedProbabilities'] = _convert_supports_config(m['predictedProbabilities'])
    else:
        raise ValueError(f"Unknown summary stats metric configuration type: {m['__typename']}")

    return res


def _convert_custom_metric(config: CustomMetricConfig) -> dict:
    return {
        'metricId': config['metric']['id'],
        'enabledEstimated': _convert_supports_config(config['estimated']),
        'enabledRealized': _convert_supports_config(config['realized']),
        'threshold': _convert_threshold(config['threshold']),
        'segmentThresholds': [_convert_segment_threshold(st) for st in config['segmentThresholds']],
    }
