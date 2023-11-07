import datetime
from typing import TypedDict


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


class RunSummary(TypedDict):
    id: str
    state: str
    scheduledFor: datetime.datetime
    startedAt: datetime.datetime
    completedAt: datetime.datetime
    ranSuccessfully: bool
