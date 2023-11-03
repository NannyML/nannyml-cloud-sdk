import io

import pandas as pd
from gql import gql

from .client import get_client

_UPLOAD_DATASET = gql("""
    mutation UploadDataset($file: Upload!) {
        upload_dataset(file: $file) {
            id
        }
    }
""")


class Data:
    @classmethod
    def upload(cls, df: pd.DataFrame) -> str:
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
            return get_client().execute(_UPLOAD_DATASET, upload_files=True, variable_values={
                'file': buffer,
            })['upload_dataset']['id']
