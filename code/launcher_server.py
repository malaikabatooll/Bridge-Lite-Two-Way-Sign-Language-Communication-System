from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import os
import sys

PORT = 5005
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_python_executable():
    venv_python = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable  # fallback, shouldn't be needed


PYTHON_EXE = get_python_executable()


class LaunchHandler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/launch":
            try:
                subprocess.Popen([PYTHON_EXE, "main.py"], cwd=PROJECT_DIR)
                self.send_response(200)
                self._cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"launched"}')
                print("Launched main.py")
            except Exception as e:
                self.send_response(500)
                self._cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(('{"status":"error","message":"%s"}' % str(e)).encode())
        else:
            self.send_response(404)
            self._cors_headers()
            self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), LaunchHandler)
    print(f"Using Python: {PYTHON_EXE}")
    print(f"Bridge Lite launcher running at http://localhost:{PORT}")
    print("Keep this terminal window open during your demo.")
    print("Press Ctrl+C to stop.")
    server.serve_forever()
