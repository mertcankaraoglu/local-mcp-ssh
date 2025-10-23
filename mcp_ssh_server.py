#!/usr/bin/env python3
"""
MCP SSH Server - Python implementation for uvx compatibility
"""
import json
import sys
import subprocess
import os
from typing import Dict, Any

class MCPSSHServer:
    def __init__(self):
        self.ssh_config = None
    
    def handle_list_tools(self) -> Dict[str, Any]:
        """Handle list tools request"""
        return {
            "tools": [
                {
                    "name": "ssh_connect",
                    "description": "Connect to SSH server",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "host": {"type": "string", "description": "SSH server address"},
                            "port": {"type": "number", "description": "SSH port (default: 22)", "default": 22},
                            "username": {"type": "string", "description": "Username"},
                            "password": {"type": "string", "description": "Password"}
                        },
                        "required": ["host", "username", "password"]
                    }
                },
                {
                    "name": "ssh_exec",
                    "description": "Execute command over SSH",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command to execute"}
                        },
                        "required": ["command"]
                    }
                },
                {
                    "name": "ssh_disconnect",
                    "description": "Close SSH connection",
                    "inputSchema": {"type": "object", "properties": {}}
                }
            ]
        }
    
    def handle_call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request"""
        if name == "ssh_connect":
            return self.ssh_connect(args)
        elif name == "ssh_exec":
            return self.ssh_exec(args)
        elif name == "ssh_disconnect":
            return self.ssh_disconnect()
        else:
            return {
                "content": [{"type": "text", "text": "Unknown tool"}],
                "isError": True
            }
    
    def ssh_connect(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to SSH server"""
        try:
            # Store connection details
            self.ssh_config = {
                "host": args["host"],
                "port": args.get("port", 22),
                "username": args["username"],
                "password": args["password"]
            }
            
            # Test connection with ssh command
            cmd = [
                "ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
                "-p", str(self.ssh_config["port"]),
                f"{self.ssh_config['username']}@{self.ssh_config['host']}",
                "echo 'Connection test successful'"
            ]
            
            # Try different authentication methods
            result = None
            
            # Method 1: Try with sshpass if available
            try:
                env = os.environ.copy()
                env["SSHPASS"] = self.ssh_config["password"]
                result = subprocess.run(
                    ["sshpass", "-e"] + cmd,
                    capture_output=True,
                    text=True,
                    timeout=15,
                    env=env
                )
            except FileNotFoundError:
                # Method 2: Try with expect script
                expect_script = f"""
spawn ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -p {self.ssh_config['port']} {self.ssh_config['username']}@{self.ssh_config['host']} "echo 'Connection test successful'"
expect "password:"
send "{self.ssh_config['password']}\\r"
expect eof
"""
                result = subprocess.run(
                    ["expect", "-c", expect_script],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            except FileNotFoundError:
                # Method 3: Simple connection test (just store config)
                return {
                    "content": [{"type": "text", "text": f"Connection config stored: {args['username']}@{args['host']} (will test on first command)"}]
                }
            
            if result and result.returncode == 0:
                return {
                    "content": [{"type": "text", "text": f"Connection successful: {args['username']}@{args['host']}"}]
                }
            else:
                return {
                    "content": [{"type": "text", "text": f"Connection error: {result.stderr if result else 'No SSH tools available'}"}],
                    "isError": True
                }
                
        except subprocess.TimeoutExpired:
            return {
                "content": [{"type": "text", "text": "Connection timeout"}],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Connection error: {str(e)}"}],
                "isError": True
            }
    
    def ssh_exec(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command on SSH server"""
        if not self.ssh_config:
            return {
                "content": [{"type": "text", "text": "Please connect first using ssh_connect"}],
                "isError": True
            }
        
        try:
            cmd = [
                "ssh", "-o", "StrictHostKeyChecking=no",
                "-p", str(self.ssh_config["port"]),
                f"{self.ssh_config['username']}@{self.ssh_config['host']}",
                args["command"]
            ]
            
            result = None
            
            # Try different authentication methods
            try:
                # Method 1: Try with sshpass if available
                env = os.environ.copy()
                env["SSHPASS"] = self.ssh_config["password"]
                result = subprocess.run(
                    ["sshpass", "-e"] + cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env=env
                )
            except FileNotFoundError:
                # Method 2: Try with expect script
                expect_script = f"""
spawn ssh -o StrictHostKeyChecking=no -p {self.ssh_config['port']} {self.ssh_config['username']}@{self.ssh_config['host']} "{args['command']}"
expect "password:"
send "{self.ssh_config['password']}\\r"
expect eof
"""
                result = subprocess.run(
                    ["expect", "-c", expect_script],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            except FileNotFoundError:
                # No SSH tools available
                result = None
            
            if result:
                output = result.stdout
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr}"
                
                return {
                    "content": [{"type": "text", "text": output or "Command completed"}]
                }
            else:
                return {
                    "content": [{"type": "text", "text": "No SSH tools available. Please install sshpass, expect, or plink."}],
                    "isError": True
                }
            
        except subprocess.TimeoutExpired:
            return {
                "content": [{"type": "text", "text": "Command timeout"}],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Command error: {str(e)}"}],
                "isError": True
            }
    
    def ssh_disconnect(self) -> Dict[str, Any]:
        """Disconnect from SSH server"""
        self.ssh_config = None
        return {
            "content": [{"type": "text", "text": "Connection closed"}]
        }

def main():
    """Main MCP server loop"""
    server = MCPSSHServer()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            
            if request.get("method") == "initialize":
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "mcp-ssh-server",
                            "version": "1.0.0"
                        }
                    }
                }))
                
            elif request.get("method") == "tools/list":
                response = server.handle_list_tools()
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }))
                
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                response = server.handle_call_tool(
                    params.get("name"),
                    params.get("arguments", {})
                )
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }))
                
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"message": str(e)}
            }))

if __name__ == "__main__":
    main()
