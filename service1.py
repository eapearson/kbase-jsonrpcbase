from jsonrpcbase import JSONRPCService, errors
from http.server import HTTPServer, BaseHTTPRequestHandler

service = JSONRPCService()
db = {}
last_id = 0


def add(notification):
    last_id = last_id + 1
    db[last_id] = notification
    return last_id


def get(id):
    if id not in db:
        raise errors.APIError(100, f'Notification not found with id {id}')
    return db[id]


def search(query):
    return [n for n in db if query in n]

 # Adds the method login to the service as a 'new' using the optional "name" parameter
service.add(add, name='new')

# Adds the method "get" to the service; the function name will become the service method.
service.add(get)

# Adds the method "search"
search.add(search)


class ServiceHandler(BaseHTTPRequestHandler):
    def doPOST(self):
        # read body
        # no method to read body?
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # assume it is a service call.
        response = service.call(body)

        self.wfile.write(response)


if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 8888), ServiceHandler)
    httpd.server_forever()
