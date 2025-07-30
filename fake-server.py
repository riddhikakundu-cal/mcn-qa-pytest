from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'message': 'Hello, this is a fake API response!'}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()


    def do_POST(self):
        if self.path == '/pulumi/account':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'id': 5, 'data': json.loads(post_data)}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/pulumi/account/MCNTesting/organization':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'id': 3, 'data': json.loads(post_data)}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()


def run(server_class=HTTPServer, handler_class=RequestHandler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Fake server running at http://localhost:{port}')
    httpd.serve_forever()


if __name__ == "__main__":
    run()
