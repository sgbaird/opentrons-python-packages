#!/usr/bin/env python3
"""
Enhanced OT-2 Flow Server with Prefect-style workflow support
Demonstrates workflow orchestration on resource-constrained hardware
"""
import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Callable, List
from datetime import datetime
import os
import sys

# Set up environment to minimize Prefect server requirements
os.environ["PREFECT_LOGGING_TO_API_ENABLED"] = "false"
os.environ["PREFECT_API_URL"] = ""

class WorkflowEngine:
    """Lightweight workflow execution engine"""
    
    def __init__(self):
        self.tasks = {}
        self.flows = {}
        
    def task(self, name: str = None):
        """Decorator to register a task"""
        def decorator(func):
            task_name = name or func.__name__
            self.tasks[task_name] = func
            return func
        return decorator
    
    def flow(self, name: str = None):
        """Decorator to register a flow"""
        def decorator(func):
            flow_name = name or func.__name__
            self.flows[flow_name] = func
            return func
        return decorator
    
    def execute_task(self, task_name: str, *args, **kwargs):
        """Execute a registered task"""
        if task_name not in self.tasks:
            raise ValueError(f"Task '{task_name}' not found")
        return self.tasks[task_name](*args, **kwargs)
    
    def execute_flow(self, flow_name: str, *args, **kwargs):
        """Execute a registered flow"""
        if flow_name not in self.flows:
            raise ValueError(f"Flow '{flow_name}' not found")
        return self.flows[flow_name](*args, **kwargs)

# Global workflow engine instance
workflow_engine = WorkflowEngine()

class OT2FlowServer:
    """Enhanced flow server with Prefect-style capabilities"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.engine = workflow_engine
        self.run_history: List[Dict] = []
        self.server_start_time = datetime.now()
        
    def execute_flow(self, flow_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a flow with comprehensive logging"""
        if flow_name not in self.engine.flows:
            return {"error": f"Flow '{flow_name}' not found", "available_flows": list(self.engine.flows.keys())}
            
        parameters = parameters or {}
        start_time = datetime.now()
        
        try:
            print(f"🚀 Starting flow '{flow_name}' with parameters: {parameters}")
            result = self.engine.execute_flow(flow_name, **parameters)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            run_record = {
                "id": len(self.run_history) + 1,
                "flow_name": flow_name,
                "parameters": parameters,
                "result": result,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "completed",
                "logs": f"Flow '{flow_name}' completed successfully"
            }
            
            self.run_history.append(run_record)
            print(f"✅ Flow '{flow_name}' completed in {duration:.3f}s")
            return run_record
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_record = {
                "id": len(self.run_history) + 1,
                "flow_name": flow_name,
                "parameters": parameters,
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "failed",
                "logs": f"Flow '{flow_name}' failed: {str(e)}"
            }
            
            self.run_history.append(error_record)
            print(f"❌ Flow '{flow_name}' failed after {duration:.3f}s: {str(e)}")
            return error_record

# Register workflow tasks and flows
@workflow_engine.task("aspirate")
def aspirate_task(volume: float, tip_type: str = "p300"):
    """Task: Aspirate liquid"""
    time.sleep(0.1)  # Simulate hardware operation
    return {
        "action": "aspirate",
        "volume_ul": volume,
        "tip_type": tip_type,
        "timestamp": datetime.now().isoformat()
    }

@workflow_engine.task("dispense")
def dispense_task(volume: float, target: str = "well_A1"):
    """Task: Dispense liquid"""
    time.sleep(0.1)  # Simulate hardware operation
    return {
        "action": "dispense",
        "volume_ul": volume,
        "target": target,
        "timestamp": datetime.now().isoformat()
    }

@workflow_engine.task("move_to")
def move_to_task(position: str):
    """Task: Move pipette to position"""
    time.sleep(0.05)  # Simulate movement
    return {
        "action": "move_to",
        "position": position,
        "timestamp": datetime.now().isoformat()
    }

@workflow_engine.task("temperature_check")
def temperature_check_task():
    """Task: Check system temperature"""
    import random
    temp = round(random.uniform(22.0, 25.0), 1)
    return {
        "action": "temperature_check",
        "temperature_c": temp,
        "status": "normal" if 20 <= temp <= 26 else "warning",
        "timestamp": datetime.now().isoformat()
    }

@workflow_engine.flow("ot2_protocol_demo")
def ot2_protocol_demo_flow(sample_count: int = 8, volume_per_sample: float = 200.0):
    """
    Complete OT-2 protocol demonstration flow
    Shows task orchestration and workflow capabilities
    """
    results = {
        "protocol": "OT-2 Demo Protocol",
        "sample_count": sample_count,
        "volume_per_sample": volume_per_sample,
        "tasks_completed": [],
        "total_volume_transferred": 0.0
    }
    
    # Initial system check
    temp_result = workflow_engine.execute_task("temperature_check")
    results["tasks_completed"].append(temp_result)
    
    # Process each sample
    for i in range(sample_count):
        sample_id = f"sample_{i+1}"
        source_well = f"A{i+1}"
        dest_well = f"B{i+1}"
        
        # Move to source
        move_result = workflow_engine.execute_task("move_to", f"plate_1_{source_well}")
        results["tasks_completed"].append(move_result)
        
        # Aspirate from source
        aspirate_result = workflow_engine.execute_task("aspirate", volume_per_sample, "p300")
        results["tasks_completed"].append(aspirate_result)
        
        # Move to destination  
        move_result = workflow_engine.execute_task("move_to", f"plate_2_{dest_well}")
        results["tasks_completed"].append(move_result)
        
        # Dispense to destination
        dispense_result = workflow_engine.execute_task("dispense", volume_per_sample, dest_well)
        results["tasks_completed"].append(dispense_result)
        
        results["total_volume_transferred"] += volume_per_sample
    
    # Final system check
    final_temp = workflow_engine.execute_task("temperature_check")
    results["tasks_completed"].append(final_temp)
    
    results["protocol_status"] = "completed"
    results["total_tasks"] = len(results["tasks_completed"])
    
    return results

@workflow_engine.flow("ot2_calibration_flow")
def ot2_calibration_flow(calibration_type: str = "pipette"):
    """OT-2 calibration workflow"""
    steps = []
    
    if calibration_type == "pipette":
        # Pipette calibration steps
        positions = ["home", "cal_block", "tip_rack_1", "tip_rack_2", "home"]
        for pos in positions:
            move_result = workflow_engine.execute_task("move_to", pos)
            steps.append(move_result)
            
            # Test aspirate/dispense at each position
            if pos.startswith("tip_rack"):
                aspirate_result = workflow_engine.execute_task("aspirate", 10.0, "p20")
                dispense_result = workflow_engine.execute_task("dispense", 10.0, "waste")
                steps.extend([aspirate_result, dispense_result])
    
    return {
        "calibration_type": calibration_type,
        "steps_completed": steps,
        "calibration_status": "passed",
        "accuracy_score": 98.5
    }

@workflow_engine.flow("ot2_maintenance_check")
def ot2_maintenance_check_flow():
    """System maintenance and diagnostics flow"""
    checks = []
    
    # Temperature monitoring
    temp_checks = []
    for i in range(5):
        temp_result = workflow_engine.execute_task("temperature_check")
        temp_checks.append(temp_result)
        time.sleep(0.1)
    
    checks.append({
        "check_type": "temperature_stability",
        "measurements": temp_checks,
        "status": "passed"
    })
    
    # Movement tests
    test_positions = ["A1", "A12", "H1", "H12", "center"]
    movement_tests = []
    for pos in test_positions:
        move_result = workflow_engine.execute_task("move_to", pos)
        movement_tests.append(move_result)
    
    checks.append({
        "check_type": "movement_accuracy",
        "positions_tested": movement_tests,
        "status": "passed"
    })
    
    return {
        "maintenance_type": "routine_diagnostics",
        "checks_performed": checks,
        "overall_status": "system_healthy",
        "next_maintenance_date": "2025-07-18"
    }

class FlowRequestHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP request handler"""
    
    def do_GET(self):
        """Handle GET requests with improved UI"""
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            flows_list = list(self.server.flow_server.engine.flows.keys())
            tasks_list = list(self.server.flow_server.engine.tasks.keys())
            history_count = len(self.server.flow_server.run_history)
            uptime = datetime.now() - self.server.flow_server.server_start_time
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>OT-2 Flow Server</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                    .section {{ margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }}
                    .flows {{ background: #e8f5e8; }}
                    .tasks {{ background: #fff3cd; }}
                    .stats {{ background: #d4edda; }}
                    ul {{ list-style-type: none; padding: 0; }}
                    li {{ background: white; margin: 5px 0; padding: 10px; border-radius: 3px; border-left: 4px solid #3498db; }}
                    .api-endpoint {{ font-family: monospace; background: #f8f9fa; padding: 5px; border-radius: 3px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🧬 OT-2 Flow Server</h1>
                    
                    <div class="section stats">
                        <h2>📊 Server Statistics</h2>
                        <p><strong>Total flow runs:</strong> {history_count}</p>
                        <p><strong>Server uptime:</strong> {str(uptime).split('.')[0]}</p>
                        <p><strong>Current time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div class="section flows">
                        <h2>🔄 Available Flows</h2>
                        <ul>
                            {''.join(f'<li><strong>{flow}</strong></li>' for flow in flows_list)}
                        </ul>
                    </div>
                    
                    <div class="section tasks">
                        <h2>⚙️ Available Tasks</h2>
                        <ul>
                            {''.join(f'<li>{task}</li>' for task in tasks_list)}
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h2>🌐 API Endpoints</h2>
                        <ul>
                            <li><span class="api-endpoint">GET /</span> - This dashboard</li>
                            <li><span class="api-endpoint">GET /flows</span> - List available flows</li>
                            <li><span class="api-endpoint">GET /tasks</span> - List available tasks</li>
                            <li><span class="api-endpoint">POST /run/&lt;flow_name&gt;</span> - Execute a flow</li>
                            <li><span class="api-endpoint">GET /history</span> - View run history</li>
                            <li><span class="api-endpoint">GET /status</span> - Server status</li>
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h2>💡 Example Usage</h2>
                        <p><strong>Run a demo protocol:</strong></p>
                        <p class="api-endpoint">curl -X POST -H "Content-Type: application/json" -d '{{"sample_count": 4, "volume_per_sample": 150.0}}' http://localhost:8080/run/ot2_protocol_demo</p>
                        
                        <p><strong>Check system status:</strong></p>
                        <p class="api-endpoint">curl http://localhost:8080/status</p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == "/flows":
            self.send_json_response(list(self.server.flow_server.engine.flows.keys()))
            
        elif self.path == "/tasks":
            self.send_json_response(list(self.server.flow_server.engine.tasks.keys()))
            
        elif self.path == "/history":
            self.send_json_response(self.server.flow_server.run_history)
            
        elif self.path == "/status":
            uptime = datetime.now() - self.server.flow_server.server_start_time
            status = {
                "server_status": "running",
                "uptime_seconds": uptime.total_seconds(),
                "total_flows": len(self.server.flow_server.engine.flows),
                "total_tasks": len(self.server.flow_server.engine.tasks),
                "total_runs": len(self.server.flow_server.run_history),
                "successful_runs": len([r for r in self.server.flow_server.run_history if r["status"] == "completed"]),
                "failed_runs": len([r for r in self.server.flow_server.run_history if r["status"] == "failed"]),
                "current_time": datetime.now().isoformat()
            }
            self.send_json_response(status)
            
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests for flow execution"""
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
        self.send_header('Access-Control-Allow-Origin', '*')
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

def main():
    """Main server function"""
    flow_server = OT2FlowServer()
    
    print("🧬 OT-2 Enhanced Flow Server")
    print("=" * 50)
    print(f"📊 Registered {len(flow_server.engine.flows)} flows:")
    for flow_name in flow_server.engine.flows.keys():
        print(f"   • {flow_name}")
    
    print(f"⚙️  Registered {len(flow_server.engine.tasks)} tasks:")
    for task_name in flow_server.engine.tasks.keys():
        print(f"   • {task_name}")
    
    print(f"\n🚀 Starting server on port {flow_server.port}")
    print(f"🌐 Access dashboard: http://localhost:{flow_server.port}")
    print(f"📡 API base URL: http://localhost:{flow_server.port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Create and start HTTP server
    server_address = ('0.0.0.0', flow_server.port)
    httpd = FlowHTTPServer(server_address, FlowRequestHandler, flow_server)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped gracefully")
        httpd.shutdown()

if __name__ == "__main__":
    main()