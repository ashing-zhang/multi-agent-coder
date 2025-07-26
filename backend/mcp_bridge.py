#!/usr/bin/env python

"""
MCP Bridge - Core Logic Implementation
This file contains the core logic for MCP server management, configuration loading,
process handling, and request processing - separated from the API interface.
"""

import os
import json
import uuid
import subprocess
import asyncio
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import shutil
import pathlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-bridge")

# Risk level constants
RISK_LEVEL = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3
}

# Risk level descriptions
RISK_LEVEL_DESCRIPTION = {
    RISK_LEVEL["LOW"]: "Low risk - Standard execution",
    RISK_LEVEL["MEDIUM"]: "Medium risk - Requires confirmation",
    RISK_LEVEL["HIGH"]: "High risk - Docker execution required"
}

# Server state management
server_processes: Dict[str, Dict] = {}
pending_confirmations: Dict[str, Dict] = {}
server_initialization_state: Dict[str, str] = {}

# Export constants and types for API module
export = {
    'RISK_LEVEL': RISK_LEVEL,
    'RISK_LEVEL_DESCRIPTION': RISK_LEVEL_DESCRIPTION,
    'server_processes': server_processes,
    'pending_confirmations': pending_confirmations,
    'server_initialization_state': server_initialization_state
}

# Helper function to load server configuration from file or environment
def load_server_config():
    logger.info("Loading server configuration...")
    config = {}

    # Try to load from config file
    config_path = os.getenv("MCP_CONFIG_PATH", os.path.join(os.getcwd(), "mcp_config.json"))
    logger.info(f"Checking for config file at: {config_path}")

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                config = config_data.get("mcpServers", {})
                logger.info(f"Loaded configuration from {config_path}: {list(config.keys())}")

                # Validate risk levels
                for server_id, server_config in config.items():
                    if "riskLevel" in server_config:
                        risk_level = server_config["riskLevel"]
                        if risk_level not in RISK_LEVEL.values():
                            logger.warning(f"Invalid risk level {risk_level} for server {server_id}, ignoring risk level")
                            del server_config["riskLevel"]
                        elif risk_level == RISK_LEVEL["HIGH"] and ("docker" not in server_config or "image" not in server_config["docker"]):
                            logger.warning(f"Server {server_id} has HIGH risk level but no docker configuration, downgrading to MEDIUM risk level")
                            server_config["riskLevel"] = RISK_LEVEL["MEDIUM"]
        else:
            logger.info(f"No configuration file found at {config_path}, using defaults or environment variables")
    except Exception as e:
        logger.error(f"Error loading configuration file: {str(e)}")

    # Allow environment variables to override config
    # Format: MCP_SERVER_NAME_COMMAND, MCP_SERVER_NAME_ARGS (comma-separated)
    for key in os.environ:
        if key.startswith("MCP_SERVER_") and key.endswith("_COMMAND"):
            server_name = key.replace("MCP_SERVER_", "").replace("_COMMAND", "").lower()
            command = os.environ[key]
            args_key = f"MCP_SERVER_{server_name.upper()}_ARGS"
            args = os.environ[args_key].split(',') if args_key in os.environ else []

            # Create or update server config
            config[server_name] = {
                "command": command,
                "args": args
            }

            # Check for environment variables
            env_key = f"MCP_SERVER_{server_name.upper()}_ENV"
            if env_key in os.environ:
                try:
                    config[server_name]["env"] = json.loads(os.environ[env_key])
                except Exception as e:
                    logger.error(f"Error parsing environment variables for {server_name}: {str(e)}")

            # Check for risk level
            risk_level_key = f"MCP_SERVER_{server_name.upper()}_RISK_LEVEL"
            if risk_level_key in os.environ:
                try:
                    risk_level = int(os.environ[risk_level_key])
                    if risk_level in RISK_LEVEL.values():
                        config[server_name]["riskLevel"] = risk_level

                        # For high risk level, check for docker configuration
                        if risk_level == RISK_LEVEL["HIGH"]:
                            docker_config_key = f"MCP_SERVER_{server_name.upper()}_DOCKER_CONFIG"
                            if docker_config_key in os.environ:
                                try:
                                    config[server_name]["docker"] = json.loads(os.environ[docker_config_key])
                                except Exception as e:
                                    logger.error(f"Error parsing docker configuration for {server_name}: {str(e)}")
                                    logger.warning(f"Server {server_name} has HIGH risk level but invalid docker configuration, downgrading to MEDIUM risk level")
                                    config[server_name]["riskLevel"] = RISK_LEVEL["MEDIUM"]
                            else:
                                logger.warning(f"Server {server_name} has HIGH risk level but no docker configuration, downgrading to MEDIUM risk level")
                                config[server_name]["riskLevel"] = RISK_LEVEL["MEDIUM"]
                    else:
                        logger.warning(f"Invalid risk level {risk_level} for server {server_name}, ignoring risk level")
                except Exception as e:
                    logger.error(f"Error parsing risk level for {server_name}: {str(e)}")

            logger.info(f"Added server from environment: {server_name}")

    logger.info(f"Loaded {len(config)} server configurations")
    return config

# Initialize and connect to MCP servers
async def init_servers():
    logger.info("Initializing MCP servers...")
    server_config = load_server_config()

    logger.info("Server configurations found:")
    logger.info(json.dumps(server_config, indent=2))

    # Start each configured server
    for server_id, config in server_config.items():
        try:
            logger.info(f"Starting server: {server_id}")
            await start_server(server_id, config)
            logger.info(f"Server {server_id} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize server {server_id}: {str(e)}")

    logger.info("All servers initialized")

# Start a specific MCP server
async def start_server(server_id: str, config: Dict[str, Any]):
    logger.info(f"Starting MCP server process: {server_id} with command: {config['command']} {config['args']}")

    # Set default risk level to undefined for backward compatibility
    risk_level = config.get("riskLevel")

    if risk_level is not None:
        logger.info(f"Server {server_id} has risk level: {risk_level} ({RISK_LEVEL_DESCRIPTION[risk_level]})")

        # For high risk level, verify docker is configured
        if risk_level == RISK_LEVEL["HIGH"]:
            if "docker" not in config or not isinstance(config["docker"], dict):
                raise Exception(f"Server {server_id} has HIGH risk level but no docker configuration")

            logger.info(f"Server {server_id} will be started in docker container")
    else:
        logger.info(f"Server {server_id} has no risk level specified - using standard execution")

    command_path = config['command']

    # If high risk, use docker
    if risk_level == RISK_LEVEL["HIGH"]:
        command_path = "docker"
        docker_args = ['run', '--rm']

        # Add any environment variables
        if "env" in config and isinstance(config["env"], dict):
            for key, value in config["env"].items():
                docker_args.extend(['-e', f"{key}={value}"])

        # Add volume mounts if specified
        if "volumes" in config["docker"] and isinstance(config["docker"]["volumes"], list):
            for volume in config["docker"]["volumes"]:
                docker_args.extend(['-v', volume])

        # Add network configuration if specified
        if "network" in config["docker"]:
            docker_args.extend(['--network', config["docker"]["network"]])

        # Add the image and command
        docker_args.append(config["docker"]["image"])

        # If original command was a specific executable, use it as the command in the container
        if config['command'] not in ['npm', 'npx']:
            docker_args.append(config['command'])

        # Add the original args
        docker_args.extend(config['args'])

        # Update args to use docker
        config = {
            **config,
            'originalCommand': config['command'],
            'command': command_path,
            'args': docker_args,
            'riskLevel': risk_level
        }

        logger.info(f"Transformed command for docker: {command_path} {docker_args}")
    # If the command is npx or npm, try to find their full paths
    elif config['command'] in ['npx', 'npm']:
        # On Windows, try to use the npm executable from standard locations
        if os.name == 'nt':
            possible_paths = [
                # Global npm installation
                os.path.join(os.getenv('APPDATA', ''), 'npm', f"{config['command']}.cmd"),
                # Node installation directory
                os.path.join(os.getenv('ProgramFiles', ''), 'nodejs', f"{config['command']}.cmd"),
                # Common Node installation location
                os.path.join('C:\Program Files\nodejs', f"{config['command']}.cmd"),
            ]

            for possible_path in possible_paths:
                if os.path.exists(possible_path):
                    logger.info(f"Found {config['command']} at {possible_path}")
                    command_path = possible_path
                    break
        else:
            # On Unix-like systems, try using which to find the command
            try:
                which_output = subprocess.check_output(['which', config['command']]).decode().strip()
                if which_output:
                    logger.info(f"Found {config['command']} at {which_output}")
                    command_path = which_output
            except Exception as e:
                logger.error(f"Error finding full path for {config['command']}: {str(e)}")

    logger.info(f"Using command path: {command_path}")

    # Special handling for Windows command prompt executables (.cmd files)
    is_windows_cmd = os.name == 'nt' and command_path.endswith('.cmd')
    actual_command = 'cmd' if is_windows_cmd else command_path
    actual_args = ['/c', command_path, *config['args']] if is_windows_cmd else config['args']

    logger.info(f"Spawning process with command: {actual_command} and args: {actual_args}")

    # Combine environment variables
    env_vars = os.environ.copy()

    # Add custom environment variables if provided
    if "env" in config and isinstance(config["env"], dict):
        logger.info(f"Adding environment variables for {server_id}: {config['env']}")
        env_vars.update(config['env'])
    else:
        logger.info(f"No custom environment variables for {server_id}")

    # Spawn the server process
    try:
        process = subprocess.Popen(
            [actual_command] + actual_args,
            env=env_vars,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=not is_windows_cmd
        )
    except Exception as e:
        logger.error(f"Failed to spawn process for {server_id}: {str(e)}")
        raise

    logger.info(f"Server process spawned for {server_id}, PID: {process.pid}")

    # Initialize the server state as 'starting'
    server_initialization_state[server_id] = 'starting'

    # Store the server process with its risk level
    server_processes[server_id] = {
        'process': process,
        'risk_level': risk_level,
        'pid': process.pid,
        'config': config
    }

    # Set up initialization handler
    async def initialization_handler():
        try:
            # Wait for initialization response with timeout
            start_time = datetime.now()
            while (datetime.now() - start_time) < timedelta(seconds=30):
                if process.stdout.closed:
                    break

                line = await asyncio.to_thread(process.stdout.readline)
                if not line:
                    await asyncio.sleep(0.1)
                    continue

                line = line.strip()
                if not line:
                    continue

                try:
                    response = json.loads(line)
                    # Check if this is the initialize response
                    if response.get('id') == 1 and response.get('result') and response['result'].get('protocolVersion'):
                        logger.info(f"Server {server_id} initialization completed successfully")

                        # Mark server as initialized
                        server_initialization_state[server_id] = 'initialized'

                        # Send initialized notification to complete the handshake
                        initialized_notification = {
                            'jsonrpc': '2.0',
                            'method': 'notifications/initialized'
                        }

                        process.stdin.write(json.dumps(initialized_notification) + '\n')
                        process.stdin.flush()
                        logger.info(f"Sent initialized notification to {server_id}")

                        # Set up regular output handler
                        async def output_handler():
                            while not process.stdout.closed:
                                line = await asyncio.to_thread(process.stdout.readline)
                                if line:
                                    logger.info(f"[{server_id}] STDOUT: {line.strip()}")

                        async def error_handler():
                            while not process.stderr.closed:
                                line = await asyncio.to_thread(process.stderr.readline)
                                if line:
                                    logger.error(f"[{server_id}] STDERR: {line.strip()}")

                        asyncio.create_task(output_handler())
                        asyncio.create_task(error_handler())
                        return
                except json.JSONDecodeError:
                    # Ignore JSON parsing errors during initialization
                    continue

            # If we get here, initialization timed out
            logger.error(f"Server {server_id} initialization timed out")
            server_initialization_state[server_id] = 'timeout'
            process.terminate()
            raise Exception(f"Server {server_id} initialization timed out")
        except Exception as e:
            logger.error(f"Error during initialization of {server_id}: {str(e)}")
            server_initialization_state[server_id] = 'error'
            process.terminate()
            raise

    # Start initialization handler
    asyncio.create_task(initialization_handler())

    # Set up process monitoring
    async def monitor_process():
        while True:
            if process.poll() is not None:
                logger.info(f"[${server_id}] Process exited with code {process.returncode}")
                server_processes.pop(server_id, None)
                server_initialization_state.pop(server_id, None)
                break
            await asyncio.sleep(1)

    asyncio.create_task(monitor_process())

# Shutdown an MCP server
async def shutdown_server(server_id: str):
    logger.info(f"Shutting down server: {server_id}")
    if server_id not in server_processes:
        logger.warning(f"Server {server_id} not found")
        return

    server_info = server_processes[server_id]
    try:
        process = server_info['process']
        logger.info(f"Killing process for {server_id} (PID: {process.pid})")
        if os.name == 'nt':
            process.send_signal(signal.CTRL_C_EVENT)
        else:
            process.terminate()
        # Wait for process to terminate
        await asyncio.to_thread(process.wait, timeout=5)
    except Exception as e:
        logger.error(f"Error killing process for {server_id}: {str(e)}")
        try:
            process.kill()
        except Exception as kill_error:
            logger.error(f"Error force killing process for {server_id}: {str(kill_error)}")

    server_processes.pop(server_id, None)
    server_initialization_state.pop(server_id, None)
    logger.info(f"Server {server_id} shutdown complete")

# MCP request handler
# 该函数用于向指定的 MCP 服务器发送请求，支持风险等级检查、确认机制，
# 并处理服务器响应，返回处理后的结果。可处理标准请求、中等风险需确认的请求，
# 以及高风险在 Docker 环境中执行的请求。
async def send_mcp_request(server_id: str, method: str, params: Dict[str, Any] = {}, confirmation_id: Optional[str] = None):
    if server_id not in server_processes:
        raise Exception(f"Server '{server_id}' not found or not connected")

    # Check initialization state
    init_state = server_initialization_state.get(server_id, 'unknown')
    if init_state != 'initialized':
        state_message = {
            'starting': 'Server is still starting up',
            'timeout': 'Server initialization timed out',
            'error': 'Server initialization failed'
        }.get(init_state, 'Server is not properly initialized')
        raise Exception(f"{state_message}. Current state: {init_state}")

    server_info = server_processes[server_id]
    process = server_info['process']
    risk_level = server_info['risk_level']
    config = server_info['config']

    # Only perform risk level checks if explicitly configured
    if risk_level is not None and risk_level == RISK_LEVEL["MEDIUM"] and method == 'tools/call' and not confirmation_id:
        # Generate a confirmation ID for this request
        pending_id = str(uuid.uuid4())
        logger.info(f"Medium risk level request for {server_id}/{method} - requires confirmation (ID: {pending_id})")

        # Store the pending confirmation
        pending_confirmations[pending_id] = {
            'server_id': server_id,
            'method': method,
            'params': params,
            'timestamp': datetime.now().timestamp()
        }

        # Return a response that requires confirmation
        return {
            'requires_confirmation': True,
            'confirmation_id': pending_id,
            'risk_level': risk_level,
            'risk_description': RISK_LEVEL_DESCRIPTION[risk_level],
            'server_id': server_id,
            'method': method,
            'tool_name': params.get('name'),
            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat()
        }

    request_id = str(uuid.uuid4())
    request = {
        'jsonrpc': '2.0',
        'id': request_id,
        'method': method,
        'params': params
    }

    logger.info(f"Sending request to {server_id}: {method} {json.dumps(params)}")

    # Send request
    try:
        process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
    except Exception as e:
        logger.error(f"Failed to send request to {server_id}: {str(e)}")
        raise

    # Wait for response with timeout
    start_time = datetime.now()
    while (datetime.now() - start_time) < timedelta(seconds=10):
        if process.stdout.closed:
            break

        # 使用 asyncio.to_thread 异步调用 process.stdout.readline() 方法，
        # 从子进程的标准输出中读取一行内容。此操作会阻塞直到读取到一行内容或流关闭，
        # 为了避免阻塞异步事件循环，使用 to_thread 方法将其放到单独的线程中执行。
        line = await asyncio.to_thread(process.stdout.readline)
        if not line:
            await asyncio.sleep(0.1)
            continue

        line = line.strip()
        if not line:
            continue

        try:
            response = json.loads(line)
            if response.get('id') == request_id:
                logger.info(f"Received response from {server_id} for request {request_id}")
                if 'error' in response:
                    raise Exception(response['error'].get('message', 'Unknown error'))

                # For high risk level, add information about docker execution
                if risk_level is not None and risk_level == RISK_LEVEL["HIGH"]:
                    result = response.get('result', {})
                    return {
                        **result,
                        'execution_environment': {
                            'risk_level': risk_level,
                            'risk_description': RISK_LEVEL_DESCRIPTION[risk_level],
                            'docker': True,
                            'docker_image': config.get('docker', {}).get('image', 'unknown')
                        }
                    }

                return response.get('result', {})
        except json.JSONDecodeError:
            continue

    raise Exception(f"Request to {server_id} timed out")

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
            server_info['risk_description'] = RISK_LEVEL_DESCRIPTION[info['risk_level']]

            if info['risk_level'] == RISK_LEVEL["HIGH"]:
                server_info['running_in_docker'] = True

        servers.append(server_info)

    return {'servers': servers}

@app.post("/servers")
async def create_server(server_config: ServerConfig):
    """Start a new MCP server with manual configuration"""
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
            response['risk_description'] = RISK_LEVEL_DESCRIPTION[server_info['risk_level']]

            if server_info['risk_level'] == RISK_LEVEL["HIGH"]:
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