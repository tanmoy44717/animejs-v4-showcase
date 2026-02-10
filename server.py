"""
Custom HTTP Server for Anime.js website
Handles URL routing for clean URLs and SPA-style navigation
"""

import http.server
import os
import sys

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class AnimeJSHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # Get the requested path
        path = self.path.split('?')[0]  # Remove query string
        
        # Check if the exact file exists
        file_path = os.path.join(DIRECTORY, path.lstrip('/'))
        
        if os.path.isfile(file_path):
            # Serve the file directly
            return super().do_GET()
            
        # V3/V2 assets fallback
        # If explicit v3/v2 asset missing, try root asset
        if path.startswith('/v3/assets/') or path.startswith('/v2/assets/'):
            # /v3/assets/css/style.css -> /assets/css/style.css
            new_path = path.replace('/v3/assets/', '/assets/', 1).replace('/v2/assets/', '/assets/', 1)
            new_file_path = os.path.join(DIRECTORY, new_path.lstrip('/'))
            if os.path.isfile(new_file_path):
                self.path = new_path
                return super().do_GET()
        
        # Try adding .html extension
        if os.path.isfile(file_path + '.html'):
            self.path = path + '.html'
            return super().do_GET()
        
        # Try serving index.html from the directory
        index_path = os.path.join(file_path, 'index.html')
        if os.path.isfile(index_path):
            self.path = path.rstrip('/') + '/index.html'
            return super().do_GET()
        
        # Route mapping for the Anime.js website
        # Map nested paths to their root HTML files
        route_map = {
            'documentation': 'documentation.html',
            'easing-editor': 'easing-editor.html',
            'learn': 'learn.html',
            'v3/documentation': 'v3/documentation.html',
            'v2/documentation': 'v2/documentation.html',
        }
        
        # Check if path starts with any known route
        clean_path = path.strip('/')
        for route, html_file in route_map.items():
            if clean_path.startswith(route):
                # Check if there's a matching file in the documentation dir
                possible_file = os.path.join(DIRECTORY, clean_path.replace('/', os.sep))
                if os.path.isfile(possible_file):
                    return super().do_GET()
                
                possible_html = possible_file + '.html'
                if os.path.isfile(possible_html):
                    self.path = '/' + clean_path + '.html'
                    return super().do_GET()
                
                # Fall back to the root route HTML file
                self.path = '/' + html_file
                return super().do_GET()
        
        # For any unmatched path ending in .html, try to find the file
        if path.endswith('.html'):
            # Try to find the basename in the root
            basename = os.path.basename(path)
            root_file = os.path.join(DIRECTORY, basename)
            if os.path.isfile(root_file):
                self.path = '/' + basename
                return super().do_GET()
        
        # Default: try serving the request normally (will 404 if not found)
        return super().do_GET()

    def log_message(self, format, *args):
        # Color-coded logging
        status = args[1] if len(args) > 1 else ''
        if '404' in str(status):
            print(f"  ❌ {args[0]}")
        elif '200' in str(status):
            print(f"  ✅ {args[0]}")
        else:
            print(f"  📄 {args[0]}")

def run():
    os.chdir(DIRECTORY)
    with http.server.HTTPServer(('', PORT), AnimeJSHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════╗
║   🎬 Anime.js Local Server              ║
║   http://localhost:{PORT}                  ║
║   Press Ctrl+C to stop                   ║
╚══════════════════════════════════════════╝
        """)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped.")

if __name__ == '__main__':
    run()
