#!/usr/bin/env python3
"""
IRIS Gate Browser Relay Server

Enables Claude in Chrome to orchestrate other AI tabs
by providing a local HTTP endpoint that aggregates tab content
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
from datetime import datetime

class RelayHandler(BaseHTTPRequestHandler):
    """Handle requests from browser extension or Claude"""
    
    def do_GET(self):
        """Return status or aggregated tab data"""
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "status": "active",
                "orchestrator": "IRIS Gate Relay v0.1",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == "/tabs":
            # Return aggregated content from all AI tabs
            # This would be populated by browser extension
            tabs_file = Path("./relay_tabs.json")
            
            if tabs_file.exists():
                with open(tabs_file) as f:
                    tabs_data = json.load(f)
            else:
                tabs_data = {"tabs": [], "message": "No tabs registered"}
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(tabs_data).encode())
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Receive commands or tab updates"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            
            if self.path == "/register_tab":
                # Register a new AI tab
                self._register_tab(data)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                response = {"status": "registered", "tab_id": data.get("tab_id")}
                self.wfile.write(json.dumps(response).encode())
            
            elif self.path == "/send_prompt":
                # Relay prompt to specific AI tab
                result = self._relay_prompt(data)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            
            else:
                self.send_error(404)
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _register_tab(self, data: dict):
        """Store tab information"""
        tabs_file = Path("./relay_tabs.json")
        
        if tabs_file.exists():
            with open(tabs_file) as f:
                tabs_data = json.load(f)
        else:
            tabs_data = {"tabs": []}
        
        # Update or add tab
        tab_id = data.get("tab_id")
        existing = next((t for t in tabs_data["tabs"] if t["tab_id"] == tab_id), None)
        
        if existing:
            existing.update(data)
        else:
            tabs_data["tabs"].append(data)
        
        with open(tabs_file, "w") as f:
            json.dump(tabs_data, f, indent=2)
    
    def _relay_prompt(self, data: dict):
        """Store prompt to be sent to AI tab"""
        queue_file = Path("./relay_queue.json")
        
        if queue_file.exists():
            with open(queue_file) as f:
                queue = json.load(f)
        else:
            queue = {"pending": []}
        
        prompt_data = {
            "target_tab": data.get("tab_id"),
            "prompt": data.get("prompt"),
            "chamber": data.get("chamber"),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        queue["pending"].append(prompt_data)
        
        with open(queue_file, "w") as f:
            json.dump(queue, f, indent=2)
        
        return {
            "status": "queued",
            "message": "Prompt queued for relay to browser extension"
        }
    
    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {format % args}")


def main():
    """Start relay server"""
    PORT = 8765
    
    print("†⟡∞ IRIS Gate Browser Relay Server")
    print(f"Listening on http://localhost:{PORT}")
    print("\nEndpoints:")
    print("  GET  /status      - Server status")
    print("  GET  /tabs        - List registered AI tabs")
    print("  POST /register_tab - Register new AI tab")
    print("  POST /send_prompt  - Queue prompt for AI tab")
    print("\nPress Ctrl+C to stop\n")
    
    server = HTTPServer(('localhost', PORT), RelayHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n†⟡∞ Server stopped")
        server.server_close()


if __name__ == "__main__":
    main()
