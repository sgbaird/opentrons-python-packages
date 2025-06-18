#!/usr/bin/env python3
"""
Simple flow serving demonstration for OT-2 without full Prefect server
This shows basic workflow orchestration and serving capabilities
"""
import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Callable
from datetime import datetime

class SimpleFlowServer:
    """A lightweight flow server for resource-constrained environments"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.flows: Dict[str, Callable] = {}
        self.run_history: list = []
        
    def register_flow(self, name: str, flow_func: Callable):
        """Register a flow function for serving"""
        self.flows[name] = flow_func
        print(f"✅ Registered flow: {name}")
        
    def execute_flow(self, flow_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a flow with given parameters"""
        if flow_name not in self.flows:
            return {"error": f"Flow '{flow_name}' not found"}
            
        parameters = parameters or {}
        start_time = datetime.now()
        
        try:
            result = self.flows[flow_name](**parameters)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            run_record = {
                "flow_name": flow_name,
                "parameters": parameters,
                "result": result,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "completed"
            }
            
            self.run_history.append(run_record)
            return run_record
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_record = {
                "flow_name": flow_name,
                "parameters": parameters,
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "failed"
            }
            
            self.run_history.append(error_record)
            return error_record

class FlowRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for flow server"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            flows_list = list(self.server.flow_server.flows.keys())
            history_count = len(self.server.flow_server.run_history)
            
            html = f"""
            <html>
            <head><title>OT-2 Flow Server</title></head>
            <body>
                <h1>🧬 OT-2 Flow Server</h1>
                <h2>Available Flows:</h2>
                <ul>
                    {''.join(f'<li>{flow}</li>' for flow in flows_list)}
                </ul>
                <h2>Statistics:</h2>
                <p>Total runs: {history_count}</p>
                <p>Server uptime: {datetime.now().isoformat()}</p>
                
                <h2>API Endpoints:</h2>
                <ul>
                    <li>GET / - This page</li>
                    <li>GET /flows - List available flows</li>
                    <li>POST /run/&lt;flow_name&gt; - Execute a flow</li>
                    <li>GET /history - View run history</li>
                </ul>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == "/flows":
            self.send_json_response(list(self.server.flow_server.flows.keys()))
            
        elif self.path == "/history":
            self.send_json_response(self.server.flow_server.run_history)
            
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith("/run/"):
            flow_name = self.path[5:]  # Remove "/run/" prefix
            
            # Parse request body for parameters
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    parameters = json.loads(post_data.decode())
                except json.JSONDecodeError:
                    parameters = {}
            else:
                parameters = {}
            
            result = self.server.flow_server.execute_flow(flow_name, parameters)
            self.send_json_response(result)
        else:
            self.send_error(404, "Not Found")
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

class FlowHTTPServer(HTTPServer):
    """Custom HTTP server that holds reference to flow server"""
    
    def __init__(self, server_address, RequestHandlerClass, flow_server):
        super().__init__(server_address, RequestHandlerClass)
        self.flow_server = flow_server

def create_and_serve_flows():
    """Create flows and serve them via HTTP"""
    
    # Create flow server
    flow_server = SimpleFlowServer()
    
    # Define some example flows
    def ot2_pipette_workflow(volume: float = 100.0, tip_type: str = "p200"):
        """Simulate OT-2 pipette workflow"""
        steps = []
        steps.append(f"Loading {tip_type} tip")
        time.sleep(0.1)  # Simulate hardware delay
        
        steps.append(f"Aspirating {volume}μL")
        time.sleep(0.2)
        
        steps.append(f"Moving to target well")
        time.sleep(0.1)
        
        steps.append(f"Dispensing {volume}μL")
        time.sleep(0.2)
        
        steps.append("Dropping tip")
        time.sleep(0.1)
        
        return {
            "workflow": "pipette_operation",
            "volume_ul": volume,
            "tip_type": tip_type,
            "steps_completed": steps,
            "total_steps": len(steps),
            "status": "success"
        }
    
    def ot2_plate_transfer(source_plate: str = "A1", dest_plate: str = "B1", sample_count: int = 8):
        """Simulate plate-to-plate transfer workflow"""
        transfers = []
        for i in range(sample_count):
            transfer = {
                "step": i + 1,
                "source": f"{source_plate}_{i+1}",
                "destination": f"{dest_plate}_{i+1}",
                "volume": 200.0,
                "timestamp": datetime.now().isoformat()
            }
            transfers.append(transfer)
            time.sleep(0.05)  # Simulate transfer time
        
        return {
            "workflow": "plate_transfer",
            "source_plate": source_plate,
            "destination_plate": dest_plate,
            "transfers_completed": transfers,
            "total_samples": sample_count,
            "status": "success"
        }
    
    def ot2_status_check():
        """Get OT-2 system status"""
        return {
            "workflow": "status_check",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "pipettes": ["p20_single_gen2", "p300_multi_gen2"],
                "deck_slots": list(range(1, 12)),
                "temperature": 23.5,
                "humidity": 45.2
            },
            "python_env": {
                "prefect_available": True,
                "version": "3.3.4"
            },
            "status": "operational"
        }
    
    # Register flows
    flow_server.register_flow("pipette_workflow", ot2_pipette_workflow)
    flow_server.register_flow("plate_transfer", ot2_plate_transfer)
    flow_server.register_flow("status_check", ot2_status_check)
    
    # Create and start HTTP server
    server_address = ('0.0.0.0', flow_server.port)
    httpd = FlowHTTPServer(server_address, FlowRequestHandler, flow_server)
    
    print(f"🚀 OT-2 Flow Server starting on port {flow_server.port}")
    print(f"📊 Registered {len(flow_server.flows)} flows")
    print(f"🌐 Access at: http://localhost:{flow_server.port}")
    print(f"📋 Available flows: {list(flow_server.flows.keys())}")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    create_and_serve_flows()