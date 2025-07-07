"""
R MCP Bridge - A clean, extensible bridge between R and MCP
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, List
import os

from fastmcp import FastMCP

# Configuration
R_API_BASE_URL = os.getenv("R_API_URL", "http://localhost:8081")
R_API_PORT = os.getenv("R_API_PORT", "8081")
TIMEOUT = httpx.Timeout(30.0, connect=5.0)

# Create FastMCP server instance
server = FastMCP("r-mcp-bridge")

# Create a reusable HTTP client
http_client = httpx.AsyncClient(base_url=R_API_BASE_URL, timeout=TIMEOUT)


class RBridgeError(Exception):
    """Custom exception for R Bridge errors"""
    pass


async def check_api_health() -> bool:
    """Check if the R API server is running"""
    try:
        response = await http_client.get("/health")
        return response.status_code == 200
    except:
        return False


async def ensure_api_running():
    """Ensure the R API is running, raise error if not"""
    if not await check_api_health():
        raise RBridgeError(
            f"R API server is not running. Please start it with: Rscript r_api.R"
        )


async def call_r_api(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic function to call R API endpoints
    
    Args:
        endpoint: API endpoint path
        payload: Request payload
        
    Returns:
        Response data as dictionary
    """
    await ensure_api_running()
    
    try:
        response = await http_client.post(endpoint, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, dict):
            return data
        else:
            # Handle non-dict responses
            import json
            return json.loads(data) if isinstance(data, str) else {"data": data}
            
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"API error: {e.response.text}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# MCP Tools

@server.tool()
async def r_status() -> Dict[str, Any]:
    """
    Check the status of the R API server
    
    Returns:
        Server status information
    """
    try:
        response = await http_client.get("/health")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "status": "offline",
            "error": str(e),
            "message": "R API server is not running"
        }


@server.tool()
async def r_hello(name: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a greeting to R
    
    Args:
        name: Name to greet (default: "World")
        
    Returns:
        Greeting message from R
    """
    payload = {}
    if name is not None:
        payload["name"] = name
    
    return await call_r_api("/api/hello", payload)


@server.tool()
async def r_add(a: float = 0, b: float = 0) -> Dict[str, Any]:
    """
    Add two numbers using R
    
    Args:
        a: First number (default: 0)
        b: Second number (default: 0)
        
    Returns:
        Addition result
    """
    return await call_r_api("/api/add", {"a": a, "b": b})


@server.tool()
async def r_stats(
    data: List[float],
    operation: str = "mean"
) -> Dict[str, Any]:
    """
    Perform statistical operations on data
    
    Args:
        data: Numeric data
        operation: One of: mean, median, sd, var, min, max, sum
        
    Returns:
        Statistical results
    """
    return await call_r_api("/api/stats", {
        "data": data,
        "operation": operation
    })


@server.tool()
async def r_lm_simple(
    x: List[float],
    y: List[float]
) -> Dict[str, Any]:
    """
    Perform simple linear regression (y ~ x)
    
    Args:
        x: Independent variable values
        y: Dependent variable values
        
    Returns:
        Regression results including coefficients, R-squared, p-values
    """
    return await call_r_api("/api/lm", {"x": x, "y": y})


# Cleanup function
async def cleanup():
    """Cleanup resources on shutdown"""
    await http_client.aclose()


# Main entry point
def main():
    """Run the MCP server"""
    import atexit
    atexit.register(lambda: asyncio.run(cleanup()))
    
    print(f"Starting R MCP Bridge Server...")
    print(f"Connecting to R API at: {R_API_BASE_URL}")
    print(f"Make sure the R API server is running: Rscript r_api.R")
    
    server.run()


if __name__ == "__main__":
    main()