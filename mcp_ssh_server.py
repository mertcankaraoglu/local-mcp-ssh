#!/usr/bin/env python3
"""
MCP SSH Server - Python implementation for uvx compatibility
"""
import asyncio
import json
import sys
import subprocess
import os
from typing import Dict, Any, Optional

class MCPSSHServer:
    def __init__(self):
        self.ssh_client = None
        self.ssh_config = None
    
    async def handle_list_tools(self) -> Dict[str, Any]:
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
    
    async def handle_call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request"""
        if name == "ssh_connect":
            return await self.ssh_connect(args)
        elif name == "ssh_exec":
            return await self.ssh_exec(args)
        elif name == "ssh_disconnect":
            return await self.ssh_disconnect()
        else:
            return {
                "content": [{"type": "text", "text": "Unknown tool"}],
                "isError": True
            }
    
    async def ssh_connect(self, args: Dict[str, Any]) -> Dict[str, Any]:
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
            
            # Use sshpass for password authentication
            env = os.environ.copy()
            env["SSHPASS"] = self.ssh_config["password"]
            
            result = subprocess.run(
                ["sshpass", "-e"] + cmd,
                capture_output=True,
                text=True,
                timeout=15,
                env=env
            )
            
            if result.returncode == 0:
                return {
                    "content": [{"type": "text", "text": f"Connection successful: {args['username']}@{args['host']}"}]
                }
            else:
                return {
                    "content": [{"type": "text", "text": f"Connection error: {result.stderr}"}],
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
    
    async def ssh_exec(self, args: Dict[str, Any]) -> Dict[str, Any]:
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
            
            env = os.environ.copy()
            env["SSHPASS"] = self.ssh_config["password"]
            
            result = subprocess.run(
                ["sshpass", "-e"] + cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            
            return {
                "content": [{"type": "text", "text": output or "Command completed"}]
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
    
    async def ssh_disconnect(self) -> Dict[str, Any]:
        """Disconnect from SSH server"""
        self.ssh_config = None
        return {
            "content": [{"type": "text", "text": "Connection closed"}]
        }

async def main():
    """Main MCP server loop"""
    server = MCPSSHServer()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            
            if request.get("method") == "tools/list":
                response = await server.handle_list_tools()
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }))
                
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                response = await server.handle_call_tool(
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
    asyncio.run(main())
