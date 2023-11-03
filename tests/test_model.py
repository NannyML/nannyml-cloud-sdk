from nannyml_cloud_sdk import model


def test_model_list_query_metches_api_schema(gql_client):
    gql_client.validate(model._LIST_QUERY)
