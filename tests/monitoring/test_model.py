from nannyml_cloud_sdk.monitoring import model


def test_model_list_query_matches_api_schema(gql_client):
    gql_client.validate(model._LIST_MODELS)


def test_model_read_query_matches_api_schema(gql_client):
    gql_client.validate(model._READ_MODEL)


def test_model_create_query_matches_api_schema(gql_client):
    gql_client.validate(model._CREATE_MODEL)


def test_model_delete_query_matches_api_schema(gql_client):
    gql_client.validate(model._DELETE_MODEL)


def test_model_get_model_data_sources_query_matches_api_schema(gql_client):
    gql_client.validate(model._GET_MODEL_DATA_SOURCES)


def test_model_get_model_data_history_query_matches_api_schema(gql_client):
    gql_client.validate(model._GET_MODEL_DATA_HISTORY)
