import http.server
import socketserver
import os

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def do_GET(self):
        # Serve index.html for root
        if self.path == '/':
            self.path = '/templates/pages/landing.html'
        # Handle static files with correct MIME types
        elif self.path.startswith('/css/'):
            try:
                with open('.' + self.path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(content)
                return
            except FileNotFoundError:
                self.send_error(404, f"File not found: {self.path}")
                return
        elif self.path.startswith('/js/'):
            try:
                with open('.' + self.path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/javascript')
                self.end_headers()
                self.wfile.write(content)
                return
            except FileNotFoundError:
                self.send_error(404, f"File not found: {self.path}")
                return
        elif self.path.startswith('/images/'):
            try:
                with open('.' + self.path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(content)
                return
            except FileNotFoundError:
                self.send_error(404, f"File not found: {self.path}")
                return
        
        # Serve HTML files from templates
        elif self.path.startswith('/templates/'):
            return super().do_GET()
        else:
            # Try to serve as HTML page
            possible_path = f'./templates/pages{self.path}.html'
            if os.path.exists(possible_path):
                self.path = f'/templates/pages{self.path}.html'
            elif self.path in ['/login', '/register', '/verify-matric', '/verify-student', 
                              '/create-password', '/forgot-password', '/dashboard']:
                self.path = f'/templates/pages{self.path}.html'
            elif self.path.startswith('/chat'):
                self.path = '/templates/pages/chat/chat_list.html'
            elif self.path.startswith('/mood'):
                self.path = '/templates/pages/mood/mood_log.html'
            elif self.path.startswith('/resources'):
                self.path = '/templates/pages/resources/resources_list.html'
            elif self.path.startswith('/assessments'):
                self.path = '/templates/pages/assessments/assessments_list.html'
            elif self.path.startswith('/settings'):
                self.path = '/templates/pages/account/settings.html'
            
        return super().do_GET()

handler = CustomHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print(f"Open your browser and navigate to: http://localhost:{PORT}")
    print("\nAvailable pages:")
    print("- Landing page: http://localhost:8000/")
    print("- Login: http://localhost:8000/login")
    print("- Dashboard: http://localhost:8000/dashboard")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.shutdown()