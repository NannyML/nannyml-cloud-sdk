import datetime
from typing import Optional

from gql import gql

from nannyml_cloud_sdk._typing import TypedDict
from nannyml_cloud_sdk.client import execute
from nannyml_cloud_sdk.enums import RunState


class RunSummary(TypedDict):
    """Summary information for NannyML analysis of a model, a `run`.

    Attributes:
        id: Unique identifier for the run (generated by NannyML Cloud).
        state: Current state of the run.
        scheduledFor: Date and time the run was scheduled to start.
        startedAt: Date and time the run started.
        completedAt: Date and time the run completed.
        ranSuccessfully: Whether the run completed successfully.
    """
    id: str
    state: RunState
    scheduledFor: Optional[datetime.datetime]
    startedAt: Optional[datetime.datetime]
    completedAt: Optional[datetime.datetime]
    ranSuccessfully: Optional[bool]


RUN_SUMMARY_FRAGMENT = f"""
    fragment RunSummary on EvaluationRun {{
        {' '.join(RunSummary.__required_keys__)}
    }}
"""


_START_RUN = gql("""
    mutation startRun($modelId: Int!) {
        start_evaluation_model_run(evaluationModelId: $modelId) {
            ...RunSummary
        }
    }
""" + RUN_SUMMARY_FRAGMENT)


class Run:
    """Operations for running NannyML model analysis."""

    @classmethod
    def trigger(cls, model_id: str) -> RunSummary:
        """Trigger analysis of new data for a model.

        This method starts analysis for a model. The run is scheduled to start immediately, but the function returns
        before the run has started. The returned summary information can be used to track the progress of the run.

        Args:
            model_id: The ID of the model to run.

        Returns:
            Summary information for the newly started run.
        """
        return execute(_START_RUN, {"modelId": int(model_id)})["start_evaluation_model_run"]