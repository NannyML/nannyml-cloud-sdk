from nannyml_cloud_sdk import model


def test_model_list_query_matches_api_schema(gql_client):
    gql_client.validate(model._LIST_QUERY)


def test_model_read_query_matches_api_schema(gql_client):
    gql_client.validate(model._READ_QUERY)


def test_model_create_query_matches_api_schema(gql_client):
    gql_client.validate(model._CREATE_MODEL)


def test_model_delete_query_matches_api_schema(gql_client):
    gql_client.validate(model._DELETE_MODEL)
