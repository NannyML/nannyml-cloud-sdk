import io
from typing import Any, Optional, TypedDict

import pandas as pd
from gql import gql

from .client import execute
from .enums import S3AuthenticationMode

_UPLOAD_DATASET = gql("""
    mutation uploadDataset($file: Upload!) {
        upload_dataset(file: $file) {
            id
        }
    }
""")


class StorageInfoRaw(TypedDict):
    """Storage info for `fsspec` compatible input, e.g. public link"""
    connectionString: str
    options: dict[str, Any]


class StorageInfoAzureBlob(TypedDict):
    """Storage info for Azure Blob Storage"""
    accountName: str
    container: str
    path: str
    isPublic: bool
    accountKey: Optional[str]
    sasToken: Optional[str]


class StorageInfoS3(TypedDict):
    """Storage info for S3"""
    uri: str
    authenticationMode: S3AuthenticationMode
    awsAccessKeyId: Optional[str]
    awsSecretAccessKey: Optional[str]


class StorageInfoCache(TypedDict):
    """Storage info for cached data"""
    id: str


class StorageInfo(TypedDict, total=False):
    """Storage info for data"""
    raw: Optional[StorageInfoRaw]
    azure: Optional[StorageInfoAzureBlob]
    s3: Optional[StorageInfoS3]
    cache: Optional[StorageInfoCache]


class Data:
    @classmethod
    def upload(cls, df: pd.DataFrame) -> StorageInfo:
        """Upload a pandas dataframe to NannyML Cloud

        Returns:
            str: The ID of the uploaded dataset
        """
        with io.BytesIO() as buffer:
            # Convert to parquet for transmission
            df.to_parquet(buffer)

            # Rewind buffer so we can transmit the file
            buffer.seek(0)

            # Set the content type so the server knows how to handle the file
            # This is the way gql expects to receive the `content-type` header, but it's not part of IOBase. Mypy
            # doesn't like the use of an unknown attribute, so we suppress mypy here.
            buffer.content_type = 'application/vnd.apache.parquet'  # type: ignore

            # Finally upload the data in parquet format
            upload = execute(_UPLOAD_DATASET, upload_files=True, variable_values={
                'file': buffer,
            })['upload_dataset']

            return {'cache': upload}
