from nannyml_cloud_sdk.experiment.schema import ExperimentSchema, Schema


def test_schema_set_metric_name_sets_column_type() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_metric_name(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'METRIC_NAME'


def test_schema_set_metric_name_unsets_existing_metric_name() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'METRIC_NAME', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_metric_name(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][1]['columnType'] == 'IGNORED'


def test_schema_set_group_name_sets_column_type() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'object', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'object', 'className': None},
        ]
    }
    new_schema = Schema.set_group_name(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'GROUP_NAME'


def test_schema_set_group_name_unsets_existing_group_name() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'GROUP_NAME', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_group_name(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][1]['columnType'] == 'IGNORED'


def test_schema_set_success_count_sets_column_type() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_success_count(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'SUCCESS_COUNT'


def test_schema_set_success_count_unsets_existing_success_count() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'SUCCESS_COUNT', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_success_count(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][1]['columnType'] == 'IGNORED'


def test_schema_set_fail_count_sets_column_type() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_fail_count(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'FAIL_COUNT'
    assert schema['columns'][0]['className'] is None


def test_schema_set_fail_count_unsets_existing_fail_count() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'float64', 'className': None},
            {'name': 'b', 'columnType': 'FAIL_COUNT', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_fail_count(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][1]['columnType'] == 'IGNORED'


def test_schema_set_ignored_sets_column_type_for_single_column() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'TARGET', 'dataType': 'float64', 'className': None},
        ]
    }
    new_schema = Schema.set_ignored(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'IGNORED'


def test_schema_set_ignored_sets_column_type_for_multiple_columns() -> None:
    schema: ExperimentSchema = {
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
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'int64', 'className': None},
            {'name': 'b', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'int64', 'className': None},
        ]
    }
    new_schema = Schema.set_identifier(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][0]['columnType'] == 'IDENTIFIER'


def test_schema_set_identifier_unsets_existing_identifier() -> None:
    schema: ExperimentSchema = {
        'columns': [
            {'name': 'a', 'columnType': 'CONTINUOUS_FEATURE', 'dataType': 'int64', 'className': None},
            {'name': 'b', 'columnType': 'IDENTIFIER', 'dataType': 'int64', 'className': None},
        ]
    }
    new_schema = Schema.set_identifier(schema, 'a')

    assert new_schema is schema
    assert schema['columns'][1]['columnType'] == 'IGNORED'
