class SdkError(Exception):
    """Base class for all exceptions raised from the NannyML Cloud SDK"""


class ApiError(SdkError):
    """Raised when the NannyML Cloud API returns an error"""


class LicenseError(SdkError):
    """Raised when the NannyML Cloud API returns a license error"""


class InvalidOperationError(SdkError):
    """Raised when attempting an invalid operation"""
