from nannyml_cloud_sdk import schema


def test_inspect_schema_query_matches_api_schema(gql_client):
    gql_client.validate(schema._INSPECT_SCHEMA)
