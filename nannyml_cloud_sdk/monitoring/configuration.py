from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, overload, Literal, Self, Generic, TypeVar

from gql import gql

from .custom_metric import CustomMetricSummary, _CUSTOM_METRIC_SUMMARY_FRAGMENT
from .enums import (
    Chunking, ClassificationRuleType, PerformanceType, UnivariateDriftMethod, MultivariateDriftMethod,
    DataQualityMetric, ConceptShiftMetric, SummaryStatsMetric
)
from .schema import ModelSchema
from .._typing import GraphQLObject, TypedDict, is_gql_type
from ..client import execute
from ..enums import PerformanceMetric, ThresholdType


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
    type: PerformanceType


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

_RUNTIME_CONFIGURATION_DETAILS_FRAGMENT = """
    fragment RuntimeConfigDetails on RuntimeConfig{
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
"""


_GET_DEFAULT_RUNTIME_CONFIGURATION = gql("""
    query getDefaultMonitoringRuntimeConfiguration($input: GetDefaultMonitoringRuntimeConfigInput!) {
        get_default_monitoring_runtime_config(input: $input) {
            ...RuntimeConfigDetails
        }
    }
""" + _THRESHOLD_FRAGMENT + _THRESHOLD_DETAILS_FRAGMENT + _CUSTOM_METRIC_SUMMARY_FRAGMENT
                                         + _RUNTIME_CONFIGURATION_DETAILS_FRAGMENT)


_GET_MODEL_RUNTIME_CONFIGURATION = gql("""
    query getModelMonitoringRuntimeConfiguration($modelId: Int!) {
        monitoring_model(id: $modelId) {
            runtimeConfig {
                ...RuntimeConfigDetails
            }
        }
    }
""" + _THRESHOLD_FRAGMENT + _THRESHOLD_DETAILS_FRAGMENT + _CUSTOM_METRIC_SUMMARY_FRAGMENT
                                       + _RUNTIME_CONFIGURATION_DETAILS_FRAGMENT)

_SET_MODEL_RUNTIME_CONFIGURATION = gql("""
    mutation setRuntimeConfiguration($modelId: Int!, $runtimeConfig: EditRuntimeConfigInput) {
      edit_monitoring_model(input: {
        modelId: $modelId,
        runtimeConfig: $runtimeConfig
        allowInvalidatingResults: true
      }) {
        __typename
      }
    }
""")


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


class _MetricConfigurationMixin:
    _d: dict[str, Any]

    @overload
    def set_threshold(self, threshold_type: Literal['CONSTANT'], lower: float, upper: float):
        ...

    @overload
    def set_threshold(
            self, threshold_type: Literal['STANDARD_DEVIATION'], std_lower_multiplier: float,
            std_upper_multiplier: float
    ):
        ...

    def set_threshold(
            self,
            threshold_type: ThresholdType,
            lower: Optional[float] = None,
            upper: Optional[float] = None,
            std_lower_multiplier: Optional[float] = None,
            std_upper_multiplier: Optional[float] = None,
    ) -> Self:
        if threshold_type == 'CONSTANT':
            self._d['threshold'] = {
                '__typename': 'ConstantThreshold',
                'lower': lower,
                'upper': upper,
            }
        elif threshold_type == 'STANDARD_DEVIATION':
            self._d['threshold'] = {
                '__typename': 'StandardDeviationThreshold',
                'stdLowerMultiplier': std_lower_multiplier,
                'stdUpperMultiplier': std_upper_multiplier,
            }
        else:
            raise ValueError(f"Unknown threshold type: {threshold_type}")

        return self

    @property
    def threshold(self) -> Optional[dict[str, Any]]:
        return self._d['threshold']

    def set_lower_value_limit(self, value: float) -> Self:
        self._d['lowerValueLimit'] = value
        return self

    @property
    def lower_value_limit(self) -> Optional[float]:
        return self._d.get('lowerValueLimit')

    def set_upper_value_limit(self, value: float) -> Self:
        self._d['upperValueLimit'] = value
        return self

    @property
    def upper_value_limit(self) -> Optional[float]:
        return self._d.get('upperValueLimit')

    def _set_default_threshold(self):
        if self._d['threshold'] is None:
            self.set_threshold('STANDARD_DEVIATION', 3, 3)


class _SimpleMetricConfigurationMixin(_MetricConfigurationMixin):
    def enable(self) -> Self:
        self._d['enabled'] = True
        self._set_default_threshold()
        return self

    def disable(self) -> Self:
        self._d['enabled'] = False
        return self


class _ColumnMetricConfigurationMixin(_MetricConfigurationMixin):
    def enable_categorical(self) -> Self:
        self._d['categorical']['enabled'] = True
        self._set_default_threshold()
        return self

    def disable_categorical(self) -> Self:
        self._d['categorical']['enabled'] = False
        return self

    def enable_continuous(self) -> Self:
        self._d['continuous']['enabled'] = True
        self._set_default_threshold()
        return self

    def disable_continuous(self) -> Self:
        self._d['continuous']['enabled'] = False
        return self

    def enable_targets(self) -> Self:
        self._d['targets']['enabled'] = True
        self._set_default_threshold()
        return self

    def disable_targets(self) -> Self:
        self._d['targets']['enabled'] = False
        return self

    def enable_predictions(self) -> Self:
        self._d['predictions']['enabled'] = True
        self._set_default_threshold()
        return self

    def disable_predictions(self) -> Self:
        self._d['predictions']['enabled'] = False
        self._set_default_threshold()
        return self

    def enable_predicted_probabilities(self) -> Self:
        self._d['predictedProbabilities']['enabled'] = True
        self._set_default_threshold()
        return self

    def disable_predicted_probabilities(self) -> Self:
        self._d['predictedProbabilities']['enabled'] = False
        return self


class _PerformanceMetricConfigurationMixin(_MetricConfigurationMixin):
    def enable_realized(self) -> Self:
        self._d['realized']['enabled'] = True
        self._set_default_threshold()
        return self

    def disable_realized(self) -> Self:
        self._d['realized']['enabled'] = False
        return self

    def enable_estimated(self) -> Self:
        self._d['estimated']['enabled'] = True
        self._set_default_threshold()
        return self

    def disable_estimated(self) -> Self:
        self._d['estimated']['enabled'] = False
        return self


T = TypeVar('T')


@dataclass
class _BaseConfiguration(Generic[T]):
    _d: T

    def to_dict(self) -> T:
        return self._d

    def __str__(self):
        return self._d.__str__()


@dataclass
class _PerformanceTypeConfiguration(_BaseConfiguration[PerformanceTypesConfiguration]):
    def enable(self) -> Self:
        self._d['enabled'] = True
        return self

    def disable(self) -> Self:
        self._d['enabled'] = False
        return self


@dataclass
class _PerformanceMetricConfiguration(
    _PerformanceMetricConfigurationMixin,
    _BaseConfiguration[PerformanceMetricsConfiguration]
):
    """Configuration of a performance metric."""


@dataclass
class _UnivariateDriftMethodConfiguration(
    _ColumnMetricConfigurationMixin,
    _BaseConfiguration[UnivariateDriftConfiguration]
):
    """Configuration of a univariate drift method."""


@dataclass
class _MultivariateDriftMethodConfiguration(
    _SimpleMetricConfigurationMixin,
    _BaseConfiguration[MultivariateDriftConfiguration]
):
    """Configuration of a multivariate drift method."""


@dataclass
class _DataQualityMetricConfiguration(
    _ColumnMetricConfigurationMixin,
    _BaseConfiguration[DataQualityMetricConfiguration]
):
    """Configuration of a data quality metric."""

    def enable_normalization(self) -> Self:
        self._d['normalize'] = True
        return self

    def disable_normalization(self) -> Self:
        self._d['normalize'] = False
        return self


@dataclass
class _ConceptShiftMetricConfiguration(
    _SimpleMetricConfigurationMixin,
    _BaseConfiguration[ConceptShiftMetricConfiguration]
):
    """Configuration of a concept shift metric."""


@dataclass
class _SummaryStatSimpleMetricConfiguration(
    _SimpleMetricConfigurationMixin,
    _BaseConfiguration[SummaryStatsSimpleMetricConfig]
):
    """Configuration of a summary statistics metric."""


@dataclass
class _SummaryStatColumnMetricConfiguration(
    _ColumnMetricConfigurationMixin,
    _BaseConfiguration[SummaryStatsColumnMetricConfig]
):
    """Configuration of a summary statistics metric."""


@dataclass
class _CustomMetricConfiguration(
    _PerformanceMetricConfigurationMixin,
    _BaseConfiguration[CustomMetricConfig]
):
    """Configuration of a custom metric."""


@dataclass
class _RuntimeConfiguration(_BaseConfiguration[RuntimeConfigurationDict]):
    def performance_type(self, name: PerformanceType) -> _PerformanceTypeConfiguration:
        t = next(t for t in self._d['performanceTypes'] if t['type'] == name)
        return _PerformanceTypeConfiguration(t)

    def performance_metric(self, name: PerformanceMetric) -> _PerformanceMetricConfiguration:
        m = next(m for m in self._d['performanceMetrics'] if m['metric'] == name)
        return _PerformanceMetricConfiguration(m)

    def univariate_drift_method(self, name: UnivariateDriftMethod) -> _UnivariateDriftMethodConfiguration:
        m = next(m for m in self._d['univariateDriftMethods'] if m['method'] == name)
        return _UnivariateDriftMethodConfiguration(m)

    def multivariate_drift_method(self, name: MultivariateDriftMethod) -> _MultivariateDriftMethodConfiguration:
        m = next(m for m in self._d['multivariateDriftMethods'] if m['method'] == name)
        return _MultivariateDriftMethodConfiguration(m)

    def data_quality_metric(self, name: DataQualityMetric) -> _DataQualityMetricConfiguration:
        m = next(m for m in self._d['dataQualityMetrics'] if m['metric'] == name)
        return _DataQualityMetricConfiguration(m)

    def concept_shift_metric(self, name: ConceptShiftMetric) -> _ConceptShiftMetricConfiguration:
        m = next(m for m in self._d['conceptShiftMetrics'] if m['metric'] == name)
        return _ConceptShiftMetricConfiguration(m)

    def summary_stat_metric(
            self, name: SummaryStatsMetric
    ) -> Union[_SummaryStatSimpleMetricConfiguration, _SummaryStatColumnMetricConfiguration]:
        m = next(m for m in self._d['summaryStatsMetrics'] if m['metric'] == name)
        if m['__typename'] == SummaryStatsSimpleMetricConfig.__name__:
            return _SummaryStatSimpleMetricConfiguration(m)
        else:
            return _SummaryStatColumnMetricConfiguration(m)

    def custom_metric(self, name: str) -> _CustomMetricConfiguration:
        m = next(m for m in self._d['customMetrics'] if m['metric']['name'] == name)
        return _CustomMetricConfiguration(m)


class RuntimeConfiguration:
    """Configuration of a monitoring model"""

    @staticmethod
    def default(
        chunking: Chunking,
        schema: ModelSchema,
        has_analysis_targets: bool,
        nr_of_rows: Optional[int] = None
    ) -> dict[str, Any]:
        rc = execute(_GET_DEFAULT_RUNTIME_CONFIGURATION, {
            'input': {
                'problemType': schema['problemType'],
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

    @staticmethod
    def _get_config(model_id: int) -> RuntimeConfigurationDict:
        rc = execute(_GET_MODEL_RUNTIME_CONFIGURATION, {
            'modelId': model_id
        })['monitoring_model']['runtimeConfig']
        return rc

    @staticmethod
    def get(model_id: int) -> _RuntimeConfiguration:
        return _RuntimeConfiguration(RuntimeConfiguration._get_config(model_id))

    @staticmethod
    def set(model_id: int, config: _RuntimeConfiguration):
        _ = execute(_SET_MODEL_RUNTIME_CONFIGURATION, {
            'modelId': model_id,
            'runtimeConfig': _to_input(config.to_dict())
        })


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
