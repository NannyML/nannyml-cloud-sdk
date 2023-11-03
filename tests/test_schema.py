import pytest
from nannyml_cloud_sdk.schema import ModelSchema, Schema, _INSPECT_SCHEMA


def test_inspect_schema_query_matches_api_schema(gql_client):
    gql_client.validate(_INSPECT_SCHEMA)


def test_schema_set_target_sets_column_type() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_target(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'TARGET'


def test_schema_set_target_unsets_existing_target() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'TARGET', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_target(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][1]['columnType'] == 'CONTINUOUS_FEATURE'


@pytest.mark.parametrize('feature_type,column_type', [
    ('CATEGORY', 'CATEGORICAL_FEATURE'),
    ('CONTINUOUS', 'CONTINUOUS_FEATURE')
])
def test_schema_set_feature_sets_column_type(feature_type, column_type) -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'IGNORED', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_feature(schema, 'a', feature_type)

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == column_type


def test_schema_set_ignored_sets_column_type_for_single_column() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'TARGET', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_ignored(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'IGNORED'


def test_schema_set_ignored_sets_column_type_for_multiple_columns() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'TARGET', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'PREDICTION', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_ignored(schema, ('a', 'b'))

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'IGNORED'
    assert schema['columns'][1]['columnType'] == 'IGNORED'


def test_schema_set_identifier_sets_column_type() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'int64', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'int64', 'className': None},
        ]
    }
    new_schema = Schema.set_identifier(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'IDENTIFIER'


def test_schema_set_identifier_unsets_existing_identifier() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'int64', 'className': None},
            {'name': 'b', 'columnType': 'IDENTIFIER', 'dataType': 'int64', 'className': None},
        ]
    }
    new_schema = Schema.set_identifier(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][1]['columnType'] == 'CONTINUOUS_FEATURE'
