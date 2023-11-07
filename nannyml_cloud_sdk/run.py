import datetime

from gql import gql

from .client import execute
from ._typing import TypedDict


class RunSummary(TypedDict):
    id: str
    state: str
    scheduledFor: datetime.datetime
    startedAt: datetime.datetime
    completedAt: datetime.datetime
    ranSuccessfully: bool


RUN_SUMMARY_FRAGMENT = f"""
    fragment RunSummary on Run {{
        {' '.join(RunSummary.__required_keys__)}
    }}
"""

_START_RUN = gql("""
    mutation startRun($modelId: Int!) {
        start_model_run(modelId: $modelId) {
            id
        }
    }
""")


class Run:
    """Operations for running NannyML model analysis"""

    @classmethod
    def trigger(cls, model_id: str) -> str:
        """Trigger analysis of new data for a model"""
        return execute(_START_RUN, {"modelId": int(model_id)})["start_model_run"]["id"]
