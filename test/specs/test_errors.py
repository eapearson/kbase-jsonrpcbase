import pytest
from jsonrpc11base.errors import InvalidResultServerError


def test_invalid_result_error():
    with pytest.raises(InvalidResultServerError) as irse:
        raise InvalidResultServerError(message='bar', path='foo', value='baz')
    assert irse.value.message == 'Invalid result'
    assert irse.value.error['message'] == 'bar'
    assert irse.value.error['path'] == 'foo'
    assert irse.value.error['value'] == 'baz'


# Invoke raw JSONRPC Errors
# TODO
