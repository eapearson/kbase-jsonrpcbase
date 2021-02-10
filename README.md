# JSONRPCBase

> NOTE: This is a fork of [level12/jsonrpc11base](https://github.com/level12/jsonrpc11base/) with changes maintained by KBase

This  is a simple JSON-RPC 1.1 library without and agnostic to a transport layer.

It features optional jsonschema validation of method parameters and results.

This library is intended as an auxiliary library for relatively easy implementation of JSON-RPC services with Unix/TCP socket
like transport protocols that do not have complex special requirements. You need to utilize some suitable transport
protocol with this library to actually provide a working JSON-RPC service.

## Features

- Easy to use, small size, well tested.
- Supports JSON-RPC v1.1 (working draft).
- Strict enforcement of JSON-RPC v1.1 spec.
- Optional argument type and return type validation.
- JSON-RPC 2.0 error codes.
    - v1.1 working draft document does not provide error code values, 
      so 2.0 error codes are at least well defined.

## Example

Example usage:

```py
import jsonrpc11, APIError, CustomServerError  from kbase_jsonrpc11base
import HTTPServer, BaseHTTPRequestHandler from http.server

service = jsonrpc11.JSONRPCService()

db = {}
last_id = 0

add(notification):
    last_id = last_id + 1
    db[last_id] = notification
    return last_id

get(id):
    if id not in db:
        raise APIError(100, f'Notification not found with id {id}')
    return db[id]

search(query):
    return [n for n in db if query i n]

 # Adds the method login to the service as a 'new' using the optional "name" parameter
service.add(add, name = 'new')

# Adds the method "get" to the service; the function name will become the service method.
service.add(get)

# Adds the method "search"
search.add(search)

class ServiceHandler(BaseHTTPRequestHandler):
    def doPOST(self):
        # read body
        body = self.body

        # assume it is a service call.
        response = service.call(body)

        self.wfile.write(response)

if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 8888), ServiceHandler)
    httpd.server_forever()
```

## Adherence (or lack thereof) to the spec

This is an implementation of [JSON-RPC 1.1 (working draft)](https://jsonrpc.org/historical/json-rpc-1-1-wd.html).

This spec was never published, and was superseded by [JSON-RPC 2.0](https://www.jsonrpc.org/specification).

The reason for the existence of this library is to support projects which are stuck on 1.1. One of these projects is [KBase](https://www.kbase.us), which has hundreds of dependencies on JSON-RPC 1.1, and therefore needs this support until (and if) it one day migrates to 2.0 or something else.

However, this library does not buy into, or can simply ignore, aspects of the 1.1 spec.

Error codes were specified as an integer between 0 and 999, but the error codes were never assigned. So instead we utilize the [error codes from JSON-RPC 2.0](https://www.jsonrpc.org/specification#error_object).

## TODO

- support banning of "system." as method prefix
- support "system.describe" (see [9. Services](https://jsonrpc.org/historical/json-rpc-1-1-wd.html#Services))

### HTTP

Since this library is transport agnostic, all implications of HTTP usage are ignored.

For instance, [RequestHeaders](https://jsonrpc.org/historical/json-rpc-1-1-wd.html#RequestHeaders) are the domain of the application using this library, not the library itself.

## Development

Install [poetry](https://python-poetry.org/) and run `poetry install`.

Run tests with `make test`.

Deploy with `poetry build` and `poetry publish`.

## Credits

This project was originally developed by Juhani Åhman.
Refactored by Jay Bolton
Refactored by Erik Pearson
