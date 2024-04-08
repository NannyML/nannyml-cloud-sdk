from nannyml_cloud_sdk.experiment import experiment


def test_experiment_list_query_matches_api_schema(gql_client):
    gql_client.validate(experiment._LIST_EXPERIMENTS)


def test_experiment_read_query_matches_api_schema(gql_client):
    gql_client.validate(experiment._READ_EXPERIMENT)


def test_experiment_create_query_matches_api_schema(gql_client):
    gql_client.validate(experiment._CREATE_EXPERIMENT)


def test_experiment_delete_query_matches_api_schema(gql_client):
    gql_client.validate(experiment._DELETE_EXPERIMENT)


def test_experiment_get_experiment_data_sources_query_matches_api_schema(gql_client):
    gql_client.validate(experiment._GET_EXPERIMENT_DATA_SOURCES)


def test_experiment_add_data_to_data_source_query_matches_api_schema(gql_client):
    gql_client.validate(experiment._ADD_DATA_TO_DATA_SOURCE)


def test_experiment_upsert_data_in_data_source_query_matches_api_schema(gql_client):
    gql_client.validate(experiment._UPSERT_DATA_IN_DATA_SOURCE)


def test_experiment_get_experiment_data_history_query_matches_api_schema(gql_client):
    gql_client.validate(experiment._GET_EXPERIMENT_DATA_HISTORY)
