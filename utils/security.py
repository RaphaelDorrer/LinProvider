from http.server import SimpleHTTPRequestHandler
from http import HTTPStatus
from socketserver import TCPServer

# Own RequestHandler class with Access Control
class SecurityHTTPRequestHandler(SimpleHTTPRequestHandler):

    # Blocks Directory Listings
    def list_directory(self, path):
        self.send_response(HTTPStatus.FORBIDDEN)
        self.end_headers()