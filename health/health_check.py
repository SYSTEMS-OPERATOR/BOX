#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

PORT = int(os.environ.get('HEALTH_PORT', '8008'))

class Handler(BaseHTTPRequestHandler):
    def _respond(self, status, body):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode('utf-8'))

    def do_GET(self):
        if self.path == '/healthz':
            body = {'status':'ok','service':'sophy-recollector'}
            self._respond(200, body)
        elif self.path == '/metrics':
            metrics = {'recollection.success': 1, 'recollection.duration_seconds': 0}
            self._respond(200, metrics)
        else:
            self._respond(404, {'error':'not found'})

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Health check running on port {PORT}')
    server.serve_forever()
