from jsonrpc11base import JSONRPCService, errors
from jsonrpc11base.service_description import ServiceDescription
from http.server import HTTPServer, BaseHTTPRequestHandler


class EntryNotFound(errors.APIError):
    code = 100
    message = "Entry not found"

    def __init__(self, id):
        self.error = {
            'id': id
        }

# A service does not need to be a class, but it probably will be
# one if it has state shared between methods.
class MyService():
    def __init__(self):
        self.db = {}
        self.last_id = 0

    def add(self, params, options):
        new_entry = params[0]
        self.last_id = self.last_id + 1
        self.db[self.last_id] = new_entry
        return self.last_id

    def get(self, params, options):
        id = params[0]
        if id not in self.db:
            raise EntryNotFound(id)
        return self.db[id]

    def search(self, params, options):
        query = params[0]
        result = []
        for key, value in self.db.items():
            if query in value:
                result.append([key, value])
        return result


# An rpc service requires a service description, which will be served
# by the built-in `system.describe` method.
description = ServiceDescription(
    'Example Database Service',
    'https://github.com/kbase/kbase-jsonrpc11base/examples/database',
    summary='An example JSON-RPC 1.1 service implementing a simple database',
    version='1.0'
)


service = JSONRPCService(description)

my_service = MyService()

# Adds the method login to the service as a 'new' using the optional "name" parameter
service.add(my_service.add, name='new')

# Adds the method "get" to the service; the function name will become the service method.
service.add(my_service.get)

# Adds the method "search"
service.add(my_service.search)

# Although this library is agnostic to the transport protocol, http is by
# far the most common (if not the only) one in use.
# In fact JSON-RPC defines it's usage with HTTP, although no other
# JSON-RPC version does, so we pretty much ignore it. E.g. we always
# return a 200 response. But those decisions are up to the
# implementation.


class ServiceHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # read body
        # no method to read body?
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # assume it is a service call.
        response = service.call(body)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        self.wfile.write(response.encode(encoding='utf_8'))


if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 8888), ServiceHandler)
    httpd.serve_forever()
