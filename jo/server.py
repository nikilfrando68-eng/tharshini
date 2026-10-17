"""
Local Full-Stack Server & AWS API Gateway / Lambda Emulator
Serves the modern frontend Single-Page Application and routes all /api/* requests
directly through the AWS Lambda handler (backend/src/lambda_handler.py).

Usage:
    python server.py
    Opens at: http://localhost:8000
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# Ensure backend package is in python path
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(WORKSPACE_DIR, "frontend")
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from backend.src.lambda_handler import lambda_handler

PORT = int(os.environ.get("PORT", 8000))

class PortalHTTPRequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_OPTIONS(self):
        """Handle CORS preflight options."""
        event = {
            "httpMethod": "OPTIONS",
            "path": self.path,
            "headers": dict(self.headers),
            "body": None
        }
        resp = lambda_handler(event)
        self.send_response(resp.get("statusCode", 200))
        for k, v in resp.get("headers", {}).items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._handle_api_request("GET")
        else:
            # SPA fallback: if file doesn't exist, serve index.html
            parsed = urllib.parse.urlparse(self.path)
            local_path = os.path.join(FRONTEND_DIR, parsed.path.lstrip("/"))
            if not os.path.exists(local_path) or os.path.isdir(local_path):
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._handle_api_request("POST")
        else:
            self.send_error(404, "Not Found")

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self._handle_api_request("PUT")
        else:
            self.send_error(404, "Not Found")

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self._handle_api_request("DELETE")
        else:
            self.send_error(404, "Not Found")

    def _handle_api_request(self, method: str):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_dict = dict(urllib.parse.parse_qsl(parsed.query)) if parsed.query else {}

        # Read body if present
        body = None
        content_len = self.headers.get("Content-Length")
        if content_len:
            try:
                body_bytes = self.rfile.read(int(content_len))
                body = body_bytes.decode("utf-8")
            except Exception:
                body = None

        # Build AWS API Gateway proxy event
        event = {
            "httpMethod": method,
            "path": path,
            "headers": dict(self.headers),
            "queryStringParameters": query_dict,
            "body": body
        }

        # Invoke AWS Lambda Handler
        result = lambda_handler(event)

        # Output response
        status = result.get("statusCode", 500)
        self.send_response(status)
        for k, v in result.get("headers", {}).items():
            self.send_header(k, v)
        self.end_headers()

        resp_body = result.get("body", "")
        if isinstance(resp_body, str):
            self.wfile.write(resp_body.encode("utf-8"))
        elif isinstance(resp_body, (dict, list)):
            self.wfile.write(json.dumps(resp_body).encode("utf-8"))

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortalHTTPRequestHandler) as httpd:
        print("=" * 70)
        print(" CAMPUS CLUB MANAGEMENT PORTAL - AWS SERVERLESS BACKEND (LOCAL)")
        print("=" * 70)
        print(f" * Server running on: http://localhost:{PORT}")
        print(f" * Serving UI from:  {FRONTEND_DIR}")
        print(" * Emulating AWS Lambda & API Gateway with Cognito/DynamoDB")
        print("\n DEMO CREDENTIALS:")
        print(" -------------------------------------------------------------")
        print(" [STUDENT - ELIGIBLE (High CGPA & Scores)]")
        print("   Register Number: 123456789012")
        print("   Password:        Student@123")
        print("   (Eligible for Coding Club, AI Club, Robotics Club, etc.)")
        print(" -------------------------------------------------------------")
        print(" [STUDENT - INELIGIBLE FOR CODING/AI (Aptitude 55, CGPA 6.8)]")
        print("   Register Number: 123456789013")
        print("   Password:        Student@123")
        print(" -------------------------------------------------------------")
        print(" [STUDENT - PENDING OFFICIAL VERIFICATION]")
        print("   Register Number: 123456789014")
        print("   Password:        Student@123")
        print(" -------------------------------------------------------------")
        print(" [CLUB LEADER - Coding Club]")
        print("   Register Number: leader_coding")
        print("   Password:        Leader@123")
        print(" -------------------------------------------------------------")
        print(" [ADMINISTRATOR - Dean of Student Affairs]")
        print("   Register Number: admin_portal")
        print("   Password:        Admin@123")
        print("=" * 70)
        print(" Press Ctrl+C to terminate the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully...")
            httpd.shutdown()

if __name__ == "__main__":
    run()
