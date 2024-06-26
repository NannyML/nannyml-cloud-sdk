import datetime
import functools
from typing import Optional, List, Dict

import pandas as pd
from gql import gql

from nannyml_cloud_sdk._typing import TypedDict
from nannyml_cloud_sdk.client import execute
from nannyml_cloud_sdk.data import DATA_SOURCE_SUMMARY_FRAGMENT, DATA_SOURCE_EVENT_FRAGMENT, Data, DataSourceSummary, \
    DataSourceEvent, _UPSERT_DATA_IN_DATA_SOURCE, _ADD_DATA_TO_DATA_SOURCE
from nannyml_cloud_sdk.experiment.enums import ExperimentType
from nannyml_cloud_sdk.experiment.run import RunSummary, RUN_SUMMARY_FRAGMENT
from nannyml_cloud_sdk.experiment.schema import ExperimentSchema


class ExperimentSummary(TypedDict):
    """Summary of an experiment.

    Attributes:
        id: Unique identifier of the experiment (generated by NannyML Cloud when an experiment is created).
        name: User-defined name of the experiment.
        createdAt: Timestamp when the experiment was created.
    """
    id: str
    name: str
    experimentType: ExperimentType
    createdAt: datetime.datetime


class ExperimentDetails(ExperimentSummary):
    """Detailed information about an experiment.

    Attributes:
        latestRun: The currently active run or latest run performed for the experiment.
            This is ``None`` if no runs have been performed yet.
    """

    latestRun: Optional[RunSummary]


_EXPERIMENT_SUMMARY_FRAGMENT = f"""
    fragment ExperimentSummary on Experiment {{
        {' '.join(ExperimentSummary.__required_keys__)}
    }}
"""

_EXPERIMENT_DETAILS_FRAGMENT = """
    fragment ExperimentDetails on Experiment {
        ...ExperimentSummary
        latestRun {
            ...RunSummary
        }
    }
""" + _EXPERIMENT_SUMMARY_FRAGMENT + RUN_SUMMARY_FRAGMENT

_LIST_EXPERIMENTS = gql("""
    query listExperiments($filter: ExperimentsFilter) {
        experiments(filter: $filter) {
            ...ExperimentSummary
        }
    }
""" + _EXPERIMENT_SUMMARY_FRAGMENT)

_READ_EXPERIMENT = gql("""
    query readExperiment($id: Int!) {
        experiment(id: $id) {
            ...ExperimentDetails
        }
    }
""" + _EXPERIMENT_DETAILS_FRAGMENT)

_GET_EXPERIMENT_DATA_SOURCES = gql("""
    query getExperimentDataSources($experimentId: Int!) {
        experiment(id: $experimentId) {
            dataSource{
              ...DataSourceSummary
            }
        }
    }
""" + DATA_SOURCE_SUMMARY_FRAGMENT)

_GET_EXPERIMENT_DATA_HISTORY = gql("""
    query getModelDataHistory($experimentId: Int!) {
        experiment(id: $experimentId) {
            dataSource{
                events {
                    ...DataSourceEvent
                }
                ...DataSourceSummary
            }
        }
    }
""" + DATA_SOURCE_SUMMARY_FRAGMENT + DATA_SOURCE_EVENT_FRAGMENT)


_CREATE_EXPERIMENT = gql("""
    mutation createExperiment($input: CreateExperimentInput!) {
        create_experiment(input: $input) {
            ...ExperimentDetails
        }
    }
""" + _EXPERIMENT_DETAILS_FRAGMENT)

_DELETE_EXPERIMENT = gql("""
    mutation deleteExperiment($id: Int!) {
        delete_experiment(id: $id) {
            id
        }
    }
""")


class MetricConfiguration(TypedDict):
    """Configuration for a metric in an experiment.

    Attributes:
        enabled: Whether the metric is enabled or disabled.
        rope_lower_bound: Lower bound of the region of practical equivalence (ROPE) for the metric.
        rope_upper_bound: Upper bound of the region of practical equivalence (ROPE) for the metric.
        hdi_width: Required width of the highest density interval (HDI) for the metric before evaluating the hypothesis.
    """
    enabled: bool
    rope_lower_bound: float
    rope_upper_bound: float
    hdi_width: float


class Experiment:

    @classmethod
    def list(
            cls, name: Optional[str] = None, experiment_type: Optional[ExperimentType] = None
    ) -> List[ExperimentSummary]:
        """List defined experiments.

        Args:
            name: Optional name filter.
            experiment_type: Optional problem type filter.

        Returns:
            List of models that match the provided filter criteria.
        """
        return execute(_LIST_EXPERIMENTS, {
            'filter': {
                'name': name,
                'experimentType': experiment_type,
            }
        })['experiments']

    @classmethod
    def get(cls, experiment_id: str) -> ExperimentDetails:
        """Get details for an experiment.

        Args:
            experiment_id: ID of the experiment to get details for.

        Returns:
            Detailed information about the experiment.
        """
        return execute(_READ_EXPERIMENT, {'id': int(experiment_id)})['experiment']

    @classmethod
    def create(
            cls,
            name: str,
            schema: ExperimentSchema,
            experiment_data: pd.DataFrame,
            experiment_type: ExperimentType,
            metrics_configuration: Dict[str, MetricConfiguration],
            key_experiment_metric: Optional[str] = None,
    ) -> ExperimentDetails:
        """Create a new experiment.

        Args:
            name: Name for the experiment.
            schema: Schema of the experiment. Typically, created using
                [Schema.from_df][nannyml_cloud_sdk.experiment.Schema.from_df].
            experiment_data: Data to be used for the experiment.
            experiment_type: Type of the experiment.
            metrics_configuration: Configuration for each metric to be used in the experiment.
            key_experiment_metric: Optional metric to be used as the key experiment metric.

        Returns:
            Detailed about the experiment once it has been created.
        """

        data_source = {
            'name': 'experiment',
            'hasReferenceData': False,
            'hasAnalysisData': True,
            'columns': schema['columns'],
            'storageInfo': Data.upload(experiment_data),
        }

        return execute(_CREATE_EXPERIMENT, {
            'input': {
                'name': name,
                'experimentType': experiment_type,
                'dataSource': data_source,
                'kem': key_experiment_metric,
                'config': {
                    'metrics': [{
                        'metric': metric,
                        'enabled': config['enabled'],
                        'ropeLowerBound': config['rope_lower_bound'],
                        'ropeUpperBound': config['rope_upper_bound'],
                        'hdiWidth': config['hdi_width'],
                    } for metric, config in metrics_configuration.items()]
                }
            },
        })['create_experiment']

    @classmethod
    def delete(cls, experiment_id: str) -> None:
        """Delete an experiment.

        Args:
            experiment_id: ID of the experiment to delete.
        """
        execute(_DELETE_EXPERIMENT, {'id': int(experiment_id)})

    @classmethod
    def add_experiment_data(cls, experiment_id: str, data: pd.DataFrame) -> None:
        """Add evaluation data to an experiment.

        Args:
            experiment_id: ID of the experiment.
            data: Data to be added.

        Note:
            This method does not update existing data. It only adds new data. If you want to update existing data,
            use [upsert_data][nannyml_cloud_sdk.experiment.Experiment.upsert_experiment_data] instead.
        """
        data_source = cls._get_experiment_data_source(experiment_id)
        execute(_ADD_DATA_TO_DATA_SOURCE, {
            'input': {
                'id': int(data_source['id']),
                'storageInfo': Data.upload(data),
            },
        })

    @classmethod
    def upsert_experiment_data(cls, experiment_id: str, data: pd.DataFrame) -> None:
        """Add or update analysis data for an experiment.

        Args:
            experiment_id: ID of the model.
            data: Data to be added/updated.

        Note:
            This method compares existing data with the new data to determine which rows to update and which to add.
            If you are certain you are only adding new data, it is recommended to use
            [add_experiment_data][nannyml_cloud_sdk.experiment.Experiment.add_experiment_data]
            instead for better performance.
        """
        data_source = cls._get_experiment_data_source(experiment_id)
        execute(_UPSERT_DATA_IN_DATA_SOURCE, {
            'input': {
                'id': int(data_source['id']),
                'storageInfo': Data.upload(data),
            },
        })

    @classmethod
    def get_data_history(cls, experiment_id: str) -> List[DataSourceEvent]:
        """Get the data history for an experiment.

        Args:
            experiment_id: ID of the experiment.

        Returns:
            List of events related to reference data for the experiment.
        """
        return execute(_GET_EXPERIMENT_DATA_HISTORY, {
            'experimentId': int(experiment_id),
        })['evaluation_model']['referenceDataSource']['events']

    @staticmethod
    @functools.lru_cache(maxsize=128)
    def _get_experiment_data_source(experimentId: str) -> DataSourceSummary:
        """Get data sources for a model"""
        return execute(_GET_EXPERIMENT_DATA_SOURCES, {
            'experimentId': int(experimentId),
        })['experiment']['dataSource']
