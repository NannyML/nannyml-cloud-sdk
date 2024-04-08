import pytest
from nannyml_cloud_sdk.model_evaluation.schema import ModelSchema, Schema


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
    assert schema['columns'][1]['columnType'] == 'IGNORED'


def test_schema_set_prediction_score_binary_classification_sets_column_type() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_prediction_score(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'PREDICTION_SCORE'
    assert schema['columns'][0]['className'] is None


def test_schema_set_prediction_score_binary_classification_unsets_existing_prediction_score() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'PREDICTION_SCORE', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_prediction_score(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][1]['columnType'] == 'IGNORED'


def test_schema_set_prediction_score_binary_classification_rejects_multiple_prediction_scores() -> None:
    schema: ModelSchema = {
        'problemType': 'BINARY_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    with pytest.raises(ValueError):
        Schema.set_prediction_score(schema, {'a': 'A'})


def test_schema_set_prediction_score_multiclass_classification_sets_column_type() -> None:
    schema: ModelSchema = {
        'problemType': 'MULTICLASS_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_prediction_score(schema, {'class_a': 'a', 'class_b': 'b'})

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'PREDICTION_SCORE'
    assert schema['columns'][0]['className'] == 'class_a'
    assert schema['columns'][1]['columnType'] == 'PREDICTION_SCORE'
    assert schema['columns'][1]['className'] == 'class_b'


def test_schema_set_prediction_score_multiclass_classification_unsets_existing_prediction_score() -> None:
    schema: ModelSchema = {
        'problemType': 'MULTICLASS_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'PREDICTION_SCORE', 'dataType': 'float64', 'className': 'class_a'},
            {'name': 'b', 'columnType': 'PREDICTION_SCORE', 'dataType': 'float64', 'className': 'class_b'},
            {'name': 'c', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'd', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_prediction_score(schema, {'class_c': 'c', 'class_d': 'd'})

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'IGNORED'
    assert schema['columns'][0]['className'] is None
    assert schema['columns'][1]['columnType'] == 'IGNORED'
    assert schema['columns'][1]['className'] is None
    assert schema['columns'][2]['columnType'] == 'PREDICTION_SCORE'
    assert schema['columns'][2]['className'] == 'class_c'
    assert schema['columns'][3]['columnType'] == 'PREDICTION_SCORE'
    assert schema['columns'][3]['className'] == 'class_d'


def test_schema_set_prediction_score_multiclass_classification_rejects_single_prediction_score() -> None:
    schema: ModelSchema = {
        'problemType': 'MULTICLASS_CLASSIFICATION',
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    with pytest.raises(ValueError):
        Schema.set_prediction_score(schema, 'a')


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
    assert schema['columns'][1]['columnType'] == 'IGNORED'
