"""
Simple Hello R MCP Bridge Server for testing
"""

import asyncio
import httpx
from typing import Dict, Any, Optional
from pathlib import Path

from fastmcp import FastMCP

# Configuration
R_API_BASE_URL = "http://localhost:8081"
TIMEOUT = httpx.Timeout(30.0, connect=5.0)

# Create FastMCP server instance
server = FastMCP("hello-r-mcp")

# Create a reusable HTTP client
http_client = httpx.AsyncClient(base_url=R_API_BASE_URL, timeout=TIMEOUT)


async def check_api_health() -> bool:
    """Check if the R API server is running"""
    try:
        response = await http_client.get("/health")
        return response.status_code == 200
    except:
        return False


@server.tool()
async def hello_r(name: Optional[str] = None) -> Dict[str, Any]:
    """
    Say hello from R! This is a simple test function to verify R MCP integration.
    
    Args:
        name: Optional name to greet (default: "World")
    
    Returns:
        Dictionary containing greeting message and R version info
    """
    # Check API health
    if not await check_api_health():
        return {
            "error": "R API server is not running. Please start it with: Rscript hello_r_api.R",
            "success": False
        }
    
    # Prepare request payload
    payload = {}
    if name:
        payload["name"] = name
    
    try:
        # Make API request
        response = await http_client.post("/api/hello", json=payload)
        response.raise_for_status()
        # Ensure we return a proper dict
        data = response.json()
        if isinstance(data, dict):
            return data
        else:
            # If somehow we got a string, try to parse it
            import json
            return json.loads(data) if isinstance(data, str) else {"data": data}
    except httpx.HTTPStatusError as e:
        return {"error": f"API error: {e.response.text}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


@server.tool()
async def check_r_status() -> Dict[str, Any]:
    """
    Check the status of the R API server.
    
    Returns:
        Dictionary containing server status information
    """
    try:
        response = await http_client.get("/health")
        response.raise_for_status()
        # Ensure we return a proper dict
        data = response.json()
        if isinstance(data, dict):
            return data
        else:
            # If somehow we got a string, try to parse it
            import json
            return json.loads(data) if isinstance(data, str) else {"data": data}
    except Exception as e:
        return {
            "status": "offline",
            "error": str(e),
            "message": "R API server is not running. Please start it with: Rscript hello_r_api.R"
        }


@server.tool()
async def add_numbers(a: float, b: float) -> Dict[str, Any]:
    """
    Add two numbers using R's arithmetic capabilities.
    
    Args:
        a: First number to add
        b: Second number to add
    
    Returns:
        Dictionary containing the result and operation details
    """
    # Check API health
    if not await check_api_health():
        return {
            "error": "R API server is not running. Please start it with: Rscript hello_r_api.R",
            "success": False
        }
    
    # Prepare request payload
    payload = {
        "a": a,
        "b": b
    }
    
    try:
        # Make API request
        response = await http_client.post("/api/add", json=payload)
        response.raise_for_status()
        # Ensure we return a proper dict
        data = response.json()
        if isinstance(data, dict):
            return data
        else:
            # If somehow we got a string, try to parse it
            import json
            return json.loads(data) if isinstance(data, str) else {"data": data}
    except httpx.HTTPStatusError as e:
        return {"error": f"API error: {e.response.text}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


# Cleanup function
async def cleanup():
    """Cleanup resources on shutdown"""
    await http_client.aclose()


# Run the server
if __name__ == "__main__":
    import atexit
    atexit.register(lambda: asyncio.run(cleanup()))
    
    print("Starting Hello R MCP Bridge Server...")
    print("Make sure the R API server is running: Rscript hello_r_api.R")
    server.run()