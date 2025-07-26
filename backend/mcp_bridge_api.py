#!/usr/bin/env python

"""
MCP Bridge API - FastAPI Interface
This file contains the RESTful API interface implementation using FastAPI,
separated from the core MCP server management logic.
"""

import os
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from .mcp_bridge import (
    load_server_config, init_servers, shutdown_server, send_mcp_request,
    server_processes, server_initialization_state, pending_confirmations
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-bridge-api")

# Initialize FastAPI application
app = FastAPI(title="MCP Bridge API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
base_model_config = {
    "json_schema_extra": {
        "examples": [
            {
                "id": "context7",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"]
            }
        ]
    }
}

class ServerConfig(BaseModel):
    id: str
    command: str
    args: List[str] = []
    env: Optional[Dict[str, str]] = None
    risk_level: Optional[int] = None
    docker: Optional[Dict[str, Any]] = None

    class Config(base_model_config):
        pass

class ToolCallRequest(BaseModel):
    arguments: Dict[str, Any]

class ConfirmationRequest(BaseModel):
    confirm: bool

# API Routes
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(init_servers())

@app.on_event("shutdown")
async def shutdown_event():
    # Shutdown all servers
    for server_id in list(server_processes.keys()):
        await shutdown_server(server_id)

@app.get("/servers")
async def get_servers():
    """Get status of all MCP servers"""
    servers = []
    for server_id, info in server_processes.items():
        # Create base server info
        server_info = {
            'id': server_id,
            'connected': True,
            'pid': info['pid'],
            'initialization_state': server_initialization_state.get(server_id, 'unknown')
        }

        # Only include risk level information if it was explicitly set
        if info['risk_level'] is not None:
            server_info['risk_level'] = info['risk_level']
            server_info['risk_description'] = info['risk_description']

            if info['risk_level'] == 3:
                server_info['running_in_docker'] = True

        servers.append(server_info)

    return {'servers': servers}

@app.post("/servers")
async def create_server(server_config: ServerConfig):
    """Start a new MCP server with manual configuration"""
    from .mcp_bridge import start_server
    server_id = server_config.id
    if server_id in server_processes:
        raise HTTPException(status_code=409, detail=f"Server with ID '{server_id}' already exists")

    config = {
        'command': server_config.command,
        'args': server_config.args,
        'env': server_config.env,
        'riskLevel': server_config.risk_level,
        'docker': server_config.docker
    }

    try:
        await start_server(server_id, config)
        # Wait for initialization to complete
        start_time = datetime.now()
        while (datetime.now() - start_time) < timedelta(seconds=30):
            state = server_initialization_state.get(server_id, 'starting')
            if state == 'initialized':
                break
            if state in ['error', 'timeout']:
                raise HTTPException(status_code=500, detail=f"Server initialization failed with state: {state}")
            await asyncio.sleep(1)

        server_info = server_processes[server_id]
        response = {
            'id': server_id,
            'status': 'connected',
            'pid': server_info['pid']
        }

        if server_info['risk_level'] is not None:
            response['risk_level'] = server_info['risk_level']
            response['risk_description'] = server_info['risk_description']

            if server_info['risk_level'] == 3:
                response['running_in_docker'] = True

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/servers/{server_id}")
async def delete_server(server_id: str):
    """Stop a running MCP server"""
    if server_id not in server_processes:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found")

    try:
        await shutdown_server(server_id)
        return {'status': 'disconnected'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers/{server_id}/tools")
async def get_server_tools(server_id: str):
    """Get list of tools for a specific MCP server"""
    try:
        result = await send_mcp_request(server_id, 'tools/list')
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/servers/{server_id}/tools/{tool_name}")
async def call_server_tool(server_id: str, tool_name: str, request_data: ToolCallRequest):
    """Execute a tool on a specific MCP server"""
    try:
        result = await send_mcp_request(server_id, 'tools/call', {
            'name': tool_name,
            'arguments': request_data.arguments
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/confirmations/{confirmation_id}")
async def confirm_request(confirmation_id: str, request_data: ConfirmationRequest):
    """Confirm or reject a medium risk level request"""
    if confirmation_id not in pending_confirmations:
        raise HTTPException(status_code=404, detail=f"Confirmation '{confirmation_id}' not found or expired")

    pending_request = pending_confirmations[confirmation_id]

    # Check if the confirmation is expired (10 minutes)
    from datetime import datetime, timedelta
    now = datetime.now().timestamp()
    if now - pending_request['timestamp'] > 10 * 60:
        pending_confirmations.pop(confirmation_id)
        raise HTTPException(status_code=410, detail=f"Confirmation '{confirmation_id}' has expired")

    if not request_data.confirm:
        pending_confirmations.pop(confirmation_id)
        return {'status': 'rejected', 'message': 'Request was rejected'}

    try:
        # Execute the confirmed request
        result = await send_mcp_request(
            pending_request['server_id'],
            pending_request['method'],
            pending_request['params'],
            confirmation_id
        )

        pending_confirmations.pop(confirmation_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers/{server_id}/resources")
async def get_server_resources(server_id: str):
    """Get list of resources for a specific MCP server"""
    try:
        result = await send_mcp_request(server_id, 'resources/list')
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers/{server_id}/resources/{resource_uri:path}")
async def get_server_resource(server_id: str, resource_uri: str):
    """Get a specific resource from an MCP server"""
    try:
        result = await send_mcp_request(server_id, 'resources/read', {
            'uri': resource_uri
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers/{server_id}/prompts")
async def get_server_prompts(server_id: str):
    """Get list of prompts for a specific MCP server"""
    try:
        result = await send_mcp_request(server_id, 'prompts/list')
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/servers/{server_id}/prompts/{prompt_name}")
async def get_server_prompt(server_id: str, prompt_name: str, request_data: Dict[str, Any]):
    """Get a specific prompt from an MCP server with arguments"""
    try:
        result = await send_mcp_request(server_id, 'prompts/get', {
            'name': prompt_name,
            'arguments': request_data
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("__main__:app", host="0.0.0.0", port=3000, reload=True)