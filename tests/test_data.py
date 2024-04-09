from nannyml_cloud_sdk import data


def test_upload_dataset_query_matches_api_schema(gql_client):
    gql_client.validate(data._UPLOAD_DATASET)


def test_add_data_to_data_source_query_matches_api_schema(gql_client):
    gql_client.validate(data._ADD_DATA_TO_DATA_SOURCE)


def test_upsert_data_in_data_source_query_matches_api_schema(gql_client):
    gql_client.validate(data._UPSERT_DATA_IN_DATA_SOURCE)
