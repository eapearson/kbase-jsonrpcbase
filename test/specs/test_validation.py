import pytest
from jsonrpc11base.validation.validation \
    import Validation, InvalidParamsError, InvalidResultServerError

SCHEMA_DIR = 'test/data/schema/test'


def test_constructor_no_dir():
    with pytest.raises(Exception) as ex:
        Validation()
    assert 'missing 1 required positional argument' in str(ex)


def test_constructor_schema_dir_is_none():
    with pytest.raises(Exception) as ex:
        Validation(None)
    assert 'schema_dir is required' in str(ex)


def test_has_params_validation():
    v = Validation(SCHEMA_DIR)
    assert v.has_params_validation('echo')


def test_has_params_validation_not():
    v = Validation(SCHEMA_DIR)
    assert v.has_params_validation('x') is False


def test_has_result_validation():
    v = Validation(SCHEMA_DIR)
    assert v.has_result_validation('echo')


def test_has_result_validation_not():
    v = Validation(SCHEMA_DIR)
    assert v.has_result_validation('x') is False


def test_has_absent_result_validation():
    v = Validation(SCHEMA_DIR)
    assert v.has_absent_result_validation('notification')


def test_has_absent_result_validation_not_exist():
    v = Validation(SCHEMA_DIR)
    assert v.has_absent_result_validation('x') is False


def test_has_absent_result_validation_not():
    v = Validation(SCHEMA_DIR)
    assert v.has_absent_result_validation('echo') is False


def test_has_absent_params_validation():
    v = Validation(SCHEMA_DIR)
    assert v.has_absent_params_validation('noparams')


def test_has_absent_params_validation_not_exist():
    v = Validation(SCHEMA_DIR)
    assert v.has_absent_params_validation('x') is False


def test_has_absent_params_validation_not():
    v = Validation(SCHEMA_DIR)
    assert v.has_absent_params_validation('echo') is False


def test_validate_absent_params():
    v = Validation(SCHEMA_DIR)
    #  The 'validate' family of methods throws errors on validation
    # failures, otherwise doesn't return anything useful.
    v.validate_absent_params('noparams')
    assert True is True


def test_validate_absent_params_not():
    """
    Test the assertion that a method should not have parameters.
    Would be called in the context in which a method call does not
    provide parameters.
    """
    v = Validation(SCHEMA_DIR)
    with pytest.raises(InvalidParamsError) as ipe:
        v.validate_absent_params('echo')
    error_json = ipe.value.to_json()
    assert error_json['error']['message'] == 'Params must be provided for this method'


def test_validate_result():
    v = Validation(SCHEMA_DIR)
    method = "hello"
    result = "hello"
    v.validate_result(method, result)
    assert True is True


def test_validate_result_not():
    v = Validation(SCHEMA_DIR)
    method = "hello"
    result = 123
    with pytest.raises(InvalidResultServerError) as irse:
        v.validate_result(method, result)
    error_json = irse.value.to_json()
    assert error_json['name'] == 'JSONRPCError'
    assert error_json['code'] == -32002
    assert error_json['message'] == 'Invalid result'
    assert error_json['error']['message'] == "123 is not of type 'string'"
    assert error_json['error']['path'] == 'type'
    assert error_json['error']['value'] == 'string'
