from nannyml_cloud_sdk.model_evaluation import model


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


def test_model_add_data_to_data_source_query_matches_api_schema(gql_client):
    gql_client.validate(model._ADD_DATA_TO_DATA_SOURCE)


def test_model_upsert_data_in_data_source_query_matches_api_schema(gql_client):
    gql_client.validate(model._UPSERT_DATA_IN_DATA_SOURCE)


def test_model_get_model_reference_data_history_query_matches_api_schema(gql_client):
    gql_client.validate(model._GET_MODEL_REFERENCE_DATA_HISTORY)


def test_model_get_model_evaluation_data_history_query_matches_api_schema(gql_client):
    gql_client.validate(model._GET_MODEL_EVALUATION_DATA_HISTORY)
