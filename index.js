#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { Client } from "ssh2";

const server = new Server(
  { name: "mcp-ssh-server", version: "1.0.0" },
  { capabilities: { tools: {}, notifications: {} } }
);

let sshClient = null;
let sshConfig = null;

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "ssh_connect",
      description: "Connect to SSH server",
      inputSchema: {
        type: "object",
        properties: {
          host: { type: "string", description: "SSH server address" },
          port: { type: "number", description: "SSH port (default: 22)", default: 22 },
          username: { type: "string", description: "Username" },
          password: { type: "string", description: "Password" }
        },
        required: ["host", "username", "password"]
      }
    },
    {
      name: "ssh_exec",
      description: "Execute command over SSH",
      inputSchema: {
        type: "object",
        properties: {
          command: { type: "string", description: "Command to execute" }
        },
        required: ["command"]
      }
    },
    {
      name: "ssh_disconnect",
      description: "Close SSH connection",
      inputSchema: { type: "object", properties: {} }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "ssh_connect") {
    return new Promise((resolve) => {
      sshClient = new Client();
      sshConfig = {
        host: args.host,
        port: args.port || 22,
        username: args.username,
        password: args.password
      };

      sshClient.on("ready", () => {
        resolve({
          content: [{ type: "text", text: `Connection successful: ${args.username}@${args.host}` }]
        });
      }).on("error", (err) => {
        resolve({
          content: [{ type: "text", text: `Connection error: ${err.message}` }],
          isError: true
        });
      }).connect(sshConfig);
    });
  }

  if (name === "ssh_exec") {
    if (!sshClient) {
      return {
        content: [{ type: "text", text: "Please connect first using ssh_connect" }],
        isError: true
      };
    }

    return new Promise((resolve) => {
      sshClient.exec(args.command, (err, stream) => {
        if (err) {
          return resolve({
            content: [{ type: "text", text: `Command error: ${err.message}` }],
            isError: true
          });
        }

        let output = "";
        let buffer = "";
        
        const sendProgress = (chunk) => {
          buffer += chunk;
          if (buffer.includes("\n") || buffer.length > 100) {
            server.notification({
              method: "notifications/progress",
              params: {
                progressToken: request.params._meta?.progressToken,
                progress: buffer
              }
            });
            buffer = "";
          }
        };

        stream.on("data", (data) => {
          const chunk = data.toString();
          output += chunk;
          sendProgress(chunk);
        });
        
        stream.stderr.on("data", (data) => {
          const chunk = data.toString();
          output += chunk;
          sendProgress(chunk);
        });
        
        stream.on("close", () => {
          if (buffer) sendProgress(buffer);
          resolve({
            content: [{ type: "text", text: output || "Command completed" }]
          });
        });
      });
    });
  }

  if (name === "ssh_disconnect") {
    if (sshClient) {
      sshClient.end();
      sshClient = null;
    }
    return {
      content: [{ type: "text", text: "Connection closed" }]
    };
  }

  return {
    content: [{ type: "text", text: "Unknown tool" }],
    isError: true
  };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main();
