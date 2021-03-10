"""
jsonrpc11base tests
"""
import json
import pytest
import jsonrpc11base
from jsonrpc11base.errors import APIError


class MyError(APIError):
    code = 123
    message = "My error"


@pytest.fixture(scope='module')
def service():
    service_description = jsonrpc11base.service_description.ServiceDescription(
        'Test Service',
        'https://github.com/kbase/kbase-jsonrpc11base/test',
        summary='An test JSON-RPC 1.1 service',
        version='1.0'
    )

    # Our service instance
    service = jsonrpc11base.JSONRPCService(
        description=service_description
    )

    # Add testing methods go the service.
    # Note that each method needs param schema in data/schema
    def subtract(params, options):
        return params[0] - params[1]

    def kwargs_subtract(params, options):
        return params['a'] - params['b']

    def square(params, options):
        return params[0] * params[0]

    def add(params, options):
        res = 0
        for value_to_add in params:
            res += value_to_add
        return res

    def hello(options):
        return "Hello world!"

    class Hello():
        def msg(self, options):
            return "Hello world!"

    def notification(params, options):
        pass

    def return_options_and_params(params, options):
        """Used to test options param"""
        return {
            'options': options,
            'params': params
        }

    def return_options_no_params(options):
        """Used to test options param without params"""
        return options

    def broken_func(options):
        raise TypeError('whoops')

    def no_validation(options):
        "This method should have no validation defined"
        return "no validation"

    def echo(params):
        return params

    def raise_my_error(params):
        raise MyError()

    service.add(subtract)
    service.add(kwargs_subtract)
    service.add(square)
    service.add(add)
    service.add(hello)
    service.add(Hello().msg, name='hello_inst')
    service.add(notification)
    service.add(notification, name="posv")
    service.add(notification, name="keyv")
    service.add(broken_func)
    service.add(return_options_and_params)
    service.add(return_options_no_params)
    service.add(no_validation)
    service.add(echo)
    service.add(raise_my_error)

    return service

# -------------------------------
# Ensure acceptable forms all work
# Happy path testing
# Note id omitted from all requests, to
# keep them simpler
# -------------------------------

# Test direct usage of call which deals with the
# actual payload, a JSON string.
#
# In most cases we test using call_py, which consumes the
# parsed request.

# Test all forms of params.
# Params may be any valid JSON, so we have a method to
# handle each one!


def test_array_param(service):
    """
    Test valid jsonrpc multiple argument calls.
    """
    res_str = service.call(
        '{"version": "1.1", "method": "subtract", "params": [42, 23]}')
    result = json.loads(res_str)
    assert result['version'] == "1.1"
    assert result['result'] == 19


def test_with_args(service):
    """
    When a method accepts no args, but they are provided,
    will ignore this fact and just return the  results.
    """
    res = service.call_py({
        "version": "1.1",
        "method": "add",
        "params": [1, 2]
    })
    assert res['result'] == 3


def test_object_param(service):
    """
    Using an object as a parameter.
    """
    result = service.call_py({
        'version': "1.1",
        'method': 'kwargs_subtract',
        'params': {'a': 42, 'b': 23}
    })
    assert result['version'] == "1.1"
    assert result['result'] == 19


def test_no_args(service):
    """
    Test valid jsonrpc no argument calls.
    """
    result = service.call_py({
        "version": "1.1",
        "method": "hello"
    })
    assert result['version'] == "1.1"
    assert result['result'] == "Hello world!"

# -------------------------------
# Calls method codes
# Since we have validation disabled, bad params
# can leak through to the method, results are
# implementation dependent.
# -------------------------------


def test_no_args_but_provided(service):
    """
    When a method accepts no args, but they are provided,
    will ignore this fact and just return the  results.
    """
    res = service.call_py({
        "version": "1.1",
        "method": "hello",
        "params": ["hi"]
    })
    assert res['error']['message'] == 'Exception calling method'
    assert res['error']['code'] == -32002
    assert res['error']['error']['exception_message'] == \
           'hello() takes 1 positional argument but 2 were given'


def test_args_but_none_provided(service):
    """
    When a method expects args, but none are provided,
    should return error.
    """
    res = service.call_py({
        "version": "1.1",
        "method": "subtract"
    })
    # assert res['result'] == 'Hello World!'
    assert res['error']['message'] == 'Exception calling method'
    assert res['error']['code'] == -32002
    assert res['error']['error']['message'] == \
           'An unexpected exception was caught executing the method'


def test_error_without_error_data(service):
    """
    Triggers error handling for an error which does not initially
    conotain an "error" dict.
    """
    res = service.call_py({
        'version': '1.1',
        'method': 'raise_my_error'
    })
    assert res['error']['message'] == 'My error'
    assert res['error']['code'] == 123

#
# def test_no_validation(service):
#     """
#     When a method expects args, but none are provided,
#     should return error.
#     """
#     res = service.call_py({
#         "version": "1.1",
#         "method": "no_validation"
#     })
#     assert res['error']['message'] == 'Invalid params'
#     assert res['error']['code'] == -32602
#     assert res['error']['error']['message'] == ('Validation is enabled, '
#                                                 'but no parameter validator was provided')
#
#
# def test_invalid_method_type(service):
#     """
#     Test the error response for a request with an invalid method field type
#     """
#     req = """
#     {
#         "version": "1.1",
#         "method": 1,
#         "params": {}
#     }
#     """
#     res = service.call(req)
#     result = json.loads(res)
#     assert result['version'] == "1.1"
#     err = result['error']
#     assert err['code'] == -32600
#     assert err['message'] == 'Invalid Request'
#     assert err['error']['message'] == "1 is not of type 'string'"
#     assert 'id' not in result
#
# #
# # Result validation
# #
#
# # If a method call may return "null";
# # in other JSON-RPC versions there is a "notification", a call which
# # returns nothing (no response at all).
# # In 1.1 it is simply a method which the api can treat as
# # a notification, e.g. by returning null.
#
#
# def test_empty_return(service):
#     """
#     Test valid jsonrpc empty return calls.
#     """
#     result = service.call_py({
#         "version": "1.1",
#         "method": "notification",
#         "params": [1, 2, 3, 4, 5],
#     })
#     assert result['version'] == "1.1"
#     assert result['result'] is None
#
# #
# # Tests of API usage
# #
#
#
# def test_options(service):
#     """
#     Test that options is passed to the function handler
#     """
#     req = '{"version": "1.1", "method": "return_options_and_params", "params": [1]}'
#     options = {'x': 1}
#     res = service.call(req, options)
#     result = json.loads(res)
#     assert result['result']['options'] == options
#     assert result['result']['params'] == [1]
#
#
# def test_options_no_params(service):
#     """
#     Test that options is passed to the function handler
#     """
#     req = '{"version": "1.1", "method": "return_options_no_params"}'
#     options = {'x': 1}
#     res = service.call(req, options)
#     result = json.loads(res)
#     assert result['result'] == options
#
#
# def test_no_args_instance_method(service):
#     """
#     Test valid jsonrpc no argument calls on a class instance method.
#     """
#     result = service.call_py({
#         "version": "1.1",
#         "method": "hello_inst"
#     })
#     assert result['version'] == "1.1"
#     assert result['result'] == "Hello world!"
#
# # In 1.1, a "notification" is just a method call for which the
# # result is ignored; 1.1 and is typically null.
# # in 1.0 a notification required a null id, in 2.0 it requires an absent id;
# # in 1.1, we don't care.
#
#
# def test_notification(service):
#     """
#     Test valid notification jsonrpc calls.
#     """
#     params = {
#         "version": "1.1",
#         "method": "notification",
#         "params": [1, 2, 3, 4, 5]
#     }
#     result_str = service.call(json.dumps(params))
#     result = json.loads(result_str)
#     assert result['version'] == "1.1"
#     assert result['result'] is None
#
# # -------------------------------
# # Test overall payload compliance
# # Violate the JSON-RPC 1.1 rules!
# # -------------------------------
#
#
# def test_parse_error(service):
#     """
#     Test parse error triggering invalid json message.
#     Note it is sensitive to the error message generated
#     by json.load(s)
#     """
#     # The structure doesn't matter, so use simplest invalid
#     # JSON.
#     req = 'x'
#     res = service.call(req)
#     result = json.loads(res)
#     assert result['version'] == "1.1"
#     assert result['error']['code'] == -32700
#     assert result['error']['message'] == 'Parse error'
#     assert result['error']['error'] == {
#         'message': "Expecting value: line 1 column 1 (char 0)"
#     }
#
#
# def test_invalid_request_type(service):
#     """
#     Test error response for an invalid request structure
#     In this case, use the valid JSON null value.
#     """
#     res = service.call("null")
#     result = json.loads(res)
#     assert result['version'] == "1.1"
#     assert result['error']['name'] == 'JSONRPCError'
#     assert result['error']['code'] == -32600
#     assert result['error']['message'] == 'Invalid Request'
#     assert result['error']['error']
#
#
# def test_method_not_found_error(service):
#     """
#     Test method not found error triggering jsonrpc calls.
#     """
#     # rpc call of non-existent method
#     result = service.call_py({
#         "version": "1.1",
#         "method": "foofoo",
#         "id": 1
#     })
#     methods = set(service.method_registry.keys())
#     assert result['version'] == "1.1"
#     assert result['error']['code'] == -32601
#     assert result['error']['message'] == 'Method not found'
#     assert set(result['error']['error']['available_methods']) == methods
#     assert result['id'] == 1
#
#
# def test_method_missing_error(service):
#     """
#     Test missing method error
#     """
#     result = service.call_py({"version": "1.1", "id": 1})
#     assert result['version'] == "1.1"
#     assert result['error']['code'] == -32600
#     assert result['error']['message'] == 'Invalid Request'
#     assert result['error']['error']['message'] == "'method' is a required property"
#
#
# def test_server_error(service):
#     """
#     Test server error triggering jsonrpc calls.
#     broken_func always raises
#     """
#     result = service.call_py({
#         "version": "1.1",
#         "method": "broken_func",
#         "id": "1"
#     })
#     assert result['version'] == "1.1"
#     assert result['id'] == "1"
#     print('last')
#     print(result)
#     assert result['error']['code'] == -32002
#     assert result['error']['message'] == 'Exception calling method'
#     errdat = result['error']['error']
#     assert errdat['message'] == 'An unexpected exception was caught executing the method'
#     assert errdat['exception_message'] == 'whoops'
#     assert errdat['method'] == 'broken_func'
#     assert 'traceback' in errdat
#     assert isinstance(errdat['traceback'], list)
#     # with open('test/data/test_server_error_traceback.regex', 'r') as fd:
#     #     traceback_regex = re.compile(fd.read(), re.MULTILINE)
#     # print(errdat['traceback'])
#     # assert traceback_regex.match(errdat['traceback'])
#
# # Actually, any json vale is okay for a 1.1 id.
#
#
# def test_invalid_id(service):
#     """
#     Test the error response for an invalid `id` field
#     """
#     params = {"version": "1.1", "id": {}, "method": "notification", "params": {}}
#     res = service.call(json.dumps(params))
#     result = json.loads(res)
#     assert result['version'] == '1.1'
#     assert result['id'] == {}
#     assert 'result' in result
#     # not testing characteristics of result
#
#
# def test_invalid_params(service):
#     """
#     Test the error response for an invalid `params` field
#     """
#     params = {"version": "1.1", "id": 0, "method": "notification", "params": "hi"}
#     res = service.call(json.dumps(params))
#     result = json.loads(res)
#     assert result['error']['message'] == 'Invalid Request'
#     assert result['error']['error']['message'] == "'hi' is not of type 'object'"
#     assert result['error']['code'] == -32600
#     assert 'result' not in result
#     assert result['id'] == 0
#
#
# def test_invalid_version(service):
#     """
#     Test error response for invalid jsonrpc version
#     """
#     # Use default
#     params = {"version": "9999", "method": "notification", "params": {"kwarg": 5}}
#     res = service.call(json.dumps(params))
#     result = json.loads(res)
#     assert result['version'] == "1.1"
#     assert result['error']['code'] == -32600
#     assert result['error']['message'] == 'Invalid Request'
#     assert result['error']['error']['message'] == "'1.1' was expected"
#
#
# def test_version_response_parse_error(service):
#     """
#     Test the jsonrpc version in the response for a parse error
#     """
#     # Parse error
#     # Assume "1.1" version because version could not be read
#     res = service.call('{ "method": "echo", "params": "bar", "baz", "id": 1} ')
#     result = json.loads(res)
#     assert result['version'] == "1.1"
#     assert result['error']['code'] == -32700
#
#
# def test_version_response_no_version(service):
#     """
#     Test the jsonrpc version in the response when no version is supplied
#     """
#     # Use default
#     res = service.call('{"method": "notification", "params": {"kwarg": 5}, "id": 6}')
#     result = json.loads(res)
#     assert result['id'] == 6
#     assert result['version'] == "1.1"
#     assert result['error']['message'] == 'Invalid Request'
#     assert result['error']['error']['message'] == "'version' is a required property"
#
#
# def test_alternate_name(service):
#     """
#     Test method calling with alternate name.
#     """
#     def hi(meta):
#         return "Hei maailma!"
#     service.add(hi, name="finnish_hello")
#     result = service.call_py({"version": "1.1", "method": "finnish_hello", "id": "1"})
#     assert result['version'] == "1.1"
#     assert result['result'] == "Hei maailma!"
#     assert result['id'] == "1"
#
#
# def test_positional_validation(service):
#     """
#     Test validation of positional arguments with valid jsonrpc calls.
#     """
#     result = service.call_py({
#         "version": "1.1",
#         "method": "posv",
#         "params": ["foo", 5, 6.0, True, False],
#         "id": "1"
#     })
#     assert result['version'] == "1.1"
#     assert result['result'] is None
#     assert result['id'] == "1"
#
#
# def test_positional_validation_error(service):
#     """
#     Test error handling of validation of positional arguments with invalid jsonrpc calls.
#     """
#     result = service.call_py({
#         "version": "1.1",
#         "id": "1",
#         "method": "posv",
#         "params": ["x", 1, 3.0, True, "x"],
#     })
#     assert result['version'] == "1.1"
#     assert result['id'] == "1"
#     assert result['error']['code'] == -32602
#     print('no message?')
#     print(result['error'])
#     assert result['error']['message'] == 'Invalid params'
#     assert result['error']['error']['message'] == "'x' is not of type 'boolean'"
#     assert result['error']['error']['path'] == 'items.4.type'
#     assert result['error']['error']['value'] == 'boolean'
#
#
# def test_keyword_validation(service):
#     """
#     Test validation of keyword arguments with valid jsonrpc calls.
#     """
#     result = service.call_py({
#         "version": "1.1",
#         "method": "keyv",
#         "params": {"a": 1, "b": False, "c": 6.0},
#         "id": "1",
#     })
#     assert result['version'] == "1.1"
#     print('RESULT', result)
#     assert result['result'] is None
#     assert result['id'] == "1"
#
#
# def test_required_keyword_validation_error(service):
#     """
#     Test error handling of validation of required keyword arguments with invalid jsonrpc calls.
#     """
#     result = service.call_py({
#         "version": "1.1",
#         "method": "keyv",
#         # Missing required property "c"
#         "params": {"a": 1, "b": 6.0},
#         "id": "1"
#     })
#     print(result)
#     assert result['version'] == "1.1"
#     assert result['error']['code'] == -32602
#     assert result['error']['message'] == 'Invalid params'
#     assert result['error']['error']['message'] == "'c' is a required property"
#     assert result['id'] == "1"
#
# # TODO: hmm .... update
# # def test_result_schema_validation(service):
# #     def echo(params, meta):
# #         return params['x']
# #     service.add(echo)
# #     with pytest.raises(jsonschema.exceptions.ValidationError):
# #         result = service.call_py({
# #             "version": "1.1",
# #             "method": "echo",
# #             "params": {"x": "hi"}
# #         })
# #         assert result['error']['error']['message'] == "'x' is not of type integer"
#
#
# def test_duplicate_method_name_err(service):
#     """
#     Test the error raised when trying to add a pre-existing method name
#     """
#     with pytest.raises(jsonrpc11base.exceptions.DuplicateMethodName) as excinfo:
#         def echo(params, options):
#             pass
#         service.add(echo)
#     assert str(excinfo.value) == 'Method "echo" already registered'
#
# # NOPE: Actually, the 2.0 spec (which we adopt for 1.1) states that the
# # user may use any code outside of the reserved range -32768 to -32000 (inclusive)
#
#
# def test_invalid_server_err_code(service):
#     """Test the error when a user sets an invalid server error code"""
#     class InvalidServerCode(jsonrpc11base.errors.APIError):
#         code = -32000
#         message = 'Invalid code!'
#
#     def invalid_server_code(meta):
#         raise InvalidServerCode
#
#     service.add(invalid_server_code)
#
#     result = service.call_py({
#         "method": "invalid_server_code",
#         "version": "1.1"
#     })
#
#     assert result['version'] == "1.1"
#     assert result['error']['code'] == -32001
#     assert result['error']['message'] == 'Reserved error code'
#     assert result['error']['error']['bad_code'] == -32000
#
# # TODO: notification with error does not throw error
# # def test_invalid_server_err_code(service):
# #     """Test the error when a user sets an invalid server error code"""
# #     class InvalidServerCode(jsonrpc11base.errors.APIError):
# #         code = -32000
# #         message = 'Invalid code!'
#
# #     def invalid_server_code(params, meta):
# #         raise InvalidServerCode
#
# #     service.add(invalid_server_code)
# #     # with pytest.raises(jsonrpc11base.errors.ServerError_ReservedErrorCode):
# #     #     service.call_py({"method": "invalid_server_code", "version": "1.1"})
#
# #     result = service.call_py({"method": "invalid_server_code", "version": "1.1"})
# #     assert result['version'] == "1.1"
# #     assert result['error']['code'] == -32001
# #     assert result['error']['message'] == 'Reserved Error Code'
# #     # assert result['error']['error']['message'] == "'x' is not of type 'boolean'"
# #     assert result['error']['error']['bad_code'] == -32000
#
# #
# # Cases covering the service description, available at "system.describe"
# #
#
#
# def test_service_discovery_ok(service):
#     """
#     Test valid service discovery response.
#     """
#     res = service.call_py({
#         "version": "1.1",
#         "id": 0,
#         "method": "system.describe",
#     })
#     assert res['version'] == '1.1'
#     assert res['id'] == 0
#     # Add builtins for assertion
#     # service_schema['definitions']['methods']['service.discover'] = {}
#     print(res)
#     assert res['result']['sdversion'] == '1.0'
#     assert res['result']['name'] == 'Test Service'
#     assert res['result']['id'] == 'https://github.com/kbase/kbase-jsonrpc11base/test'
