from typing import Optional
from jsonrpc11base.types import Identifier


# ===============================================================================
# Errors
#
# The error-codes -32768 .. -32000 (inclusive) are reserved for pre-defined
# errors.
#
# Any error-code within this range not defined explicitly below is reserved
# for future use
# ===============================================================================

# Reference: https://www.jsonrpc.org/specification#error_object
RPC_ERRORS = {
    # Invalid JSON was received. An error occurred on the server while parsing the JSON text.
    -32700: 'Parse error',
    # The JSON sent is not a valid Request object.
    -32600: 'Invalid Request',
    # The method does not exist / is not available.
    -32601: 'Method not found',
    # Invalid method parameter(s).
    -32602: 'Invalid params',
    # Internal JSON-RPC error.
    -32603: 'Internal error',
    # -32000 to -32099 to Reserved for implementation-defined server-errors.
    # Unspecified, but should have it's own error message
    -32000: 'Server error'
}


class JSONRPCError(Exception):
    """
    JSONRPCError class based on the JSON-RPC 2.0 specs.

    code - number
    message - string
    data - object
    """
    code: int = 0
    message: Optional[str] = None
    data: Optional[dict] = None

    def __init__(self, message=None):
        """Setup the Exception and overwrite the default message."""
        if message is not None:
            self.message = message

    def to_json(self):
        """Return the Exception data in a format for JSON-RPC."""

        error = {'name': 'JSONRPCError',
                 'code': self.code,
                 'message': str(self.message)}

        if self.data is not None:
            error['error'] = self.data

        return error

# Standard Errors


class ParseError(JSONRPCError):
    """Invalid JSON. An error occurred on the server while parsing the JSON text."""
    code = -32700
    message = 'Parse error'


class InvalidRequestError(JSONRPCError):
    """The received JSON is not a valid JSON-RPC Request."""
    code = -32600
    message = 'Invalid request'


class MethodNotFoundError(JSONRPCError):
    """The requested remote-procedure does not exist / is not available."""
    code = -32601
    message = 'Method not found'


class InvalidParamsError(JSONRPCError):
    """Invalid method parameters."""
    code = -32602
    message = 'Invalid params'

    def __init__(self, data=None):
        self.data = data


class InternalError(JSONRPCError):
    """Internal JSON-RPC error."""
    code = -32603
    message = 'Internal error'

# -32099..-32000 Server error. Reserved for implementation-defined server-errors.


class ServerError(JSONRPCError):
    """Generic server error."""
    code = -32000
    message = 'Server error'

# Custom Server Errors
# The server may specify any additional errors from -32002 to -32099.
# We use -32001 below.


class CustomServerError(JSONRPCError):
    """Custom server error -32001 through -32099"""
    pass


class ServerError_ReservedErrorCode(CustomServerError):
    """Generic server error."""
    code = -32001
    message = 'Reserved Error Code'

    def __init__(self, bad_code):
        self.data = {
            'bad_code': bad_code
        }


class ServerError_InvalidResult(CustomServerError):
    """Generic server error."""
    code = -32002
    message = 'Invalid result'

    def __init__(self, bad_result):
        self.data = {
            'bad_result': bad_result
        }

# The api may use any error code outside this range.
# The api should subclass the APIError exception.


class APIError(Exception):
    """
    JSONRPCError class based on the JSON-RPC 2.0 specs.

    code - number
    message - string
    data - object
    """
    code: int = 0
    message: Optional[str] = None
    data: Optional[dict] = None

    def __init__(self, message=None):
        """Setup the Exception and overwrite the default message."""
        if message is not None:
            self.message = message

    def to_json(self):
        """Return the Exception data in a format for JSON-RPC."""

        error = {'name': 'APIError',
                 'code': self.code,
                 'message': str(self.message)}

        if self.data is not None:
            error['error'] = self.data

        return error


# Non JSONRPC Errors
# TODO: convert to jsonrpc errors!!!

class InvalidJSON(Exception):
    """Invalid JSON syntax."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class InvalidParameters(Exception):
    """
    Invalid request parameters.
    Saves the JSON RPC request ID and a jsonschema validation error object.
    """

    def __init__(self, jsonschema_err, request_id):
        self.request_id = request_id
        self.jsonschema_err = jsonschema_err

    def __str__(self):
        return self.msg


class UnknownMethod(Exception):
    """Unrecognized RPC method."""

    def __init__(self, method, request_id):
        self.method = method
        self.request_id = request_id


class UnauthorizedAccess(Exception):
    """Authentication failed for an authorization header."""

    def __init__(self, auth_url, response):
        self.auth_url = auth_url
        self.response = response


def make_jsonrpc_error(code: int,
                       message: Optional[str] = None,
                       error: Optional[dict] = None):
    """
    Makes a JRON-RPC 1.1. compliant error
    """
    error_message = message or RPC_ERRORS[code]
    # disable for nowo
    # if error_message is None:
    #     return make_jsonrpc_error(-32000,
    #                               message=
    #                               error={
    #                                   'message': (f'Error id {id} not standard, '
    #                                               'so requires an error message')
    #                               })

    jsonrpc_error = {
        'name': 'JSONRPCError',
        'code': code,
        'message': error_message
    }

    if error is not None:
        jsonrpc_error['error'] = error

    return jsonrpc_error


def make_jsonrpc_error_response(error: Optional[dict],
                                id: Optional[Identifier] = None):
    """
    Makes a JRON-RPC 1.1. compliant error
    """

    response_data = {
        'version': '1.1',
        'error': error
    }

    if id is not None:
        response_data['id'] = id

    return response_data
