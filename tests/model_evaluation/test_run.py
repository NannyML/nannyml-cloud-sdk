from nannyml_cloud_sdk.model_evaluation import run


def test_run_start_query_matches_api_schema(gql_client):
    gql_client.validate(run._START_RUN)
