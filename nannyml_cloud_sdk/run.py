import datetime
from typing import TypedDict

from gql import gql

from .client import get_client


RUN_SUMMARY_FRAGMENT = """
    fragment RunSummary on Run {
        id
        state
        scheduledFor
        startedAt
        completedAt
        ranSuccessfully
    }
"""

_START_RUN = gql("""
    mutation startRun($modelId: Int!) {
        start_model_run(modelId: $modelId) {
            id
        }
    }
""")


class RunSummary(TypedDict):
    id: str
    state: str
    scheduledFor: datetime.datetime
    startedAt: datetime.datetime
    completedAt: datetime.datetime
    ranSuccessfully: bool


class Run:
    """Operations for running NannyML model analysis"""

    @classmethod
    def trigger(cls, model_id: str) -> str:
        """Trigger analysis of new data for a model"""
        return get_client().execute(_START_RUN, {"modelId": int(model_id)})["start_model_run"]["id"]
