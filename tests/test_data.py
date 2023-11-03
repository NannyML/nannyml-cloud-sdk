from nannyml_cloud_sdk import data


def test_upload_dataset_query_matches_api_schema(gql_client):
    gql_client.validate(data._UPLOAD_DATASET)
