import pytest
from jsonrpc11base.validation.schema import Schema, SchemaError


def test_schema_no_dir():
    with pytest.raises(Exception) as ex:
        Schema()
    assert 'missing 1 required positional argument' in str(ex)


def test_schema_schema_dir_is_none():
    with pytest.raises(Exception) as ex:
        Schema(None)
    assert 'schema_dir is required' in str(ex)


def test_schema_validate_absent():
    schema = Schema('test/data/schema')
    assert schema.validate_absent('foo') is False


def test_schema_validate_missing():
    schema = Schema('test/data/schema')
    with pytest.raises(SchemaError) as se:
        schema.validate('foo', 'bar')
    assert 'Schema "foo" does not exist' in str(se)


def test_schema_validate_but_absent():
    schema = Schema('test/data/schema')
    with pytest.raises(SchemaError) as se:
        schema.validate('absent', 'bar')
    assert 'Schema "absent" specifies the the value must be absent' in str(se)
