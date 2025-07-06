"""
R MCP Bridge - A clean, extensible bridge between R and MCP
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
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
            f"R API server is not running. Please start it with: Rscript base_r_api.R"
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
async def r_execute(code: str) -> Dict[str, Any]:
    """
    Execute arbitrary R code
    
    Args:
        code: R code to execute
        
    Returns:
        Execution result and output
    """
    return await call_r_api("/api/execute", {"code": code})


@server.tool()
async def r_call(
    func: str,
    args: Optional[Union[List[Any], Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Call an R function with arguments
    
    Args:
        func: Name of the R function to call
        args: Arguments to pass to the function (list or dict)
        
    Returns:
        Function result
    """
    payload = {"func": func}
    if args is not None:
        payload["args"] = args
    
    return await call_r_api("/api/call", payload)


@server.tool()
async def r_stats(
    data: List[float],
    operation: str = "summary"
) -> Dict[str, Any]:
    """
    Perform statistical operations on data
    
    Args:
        data: Numeric data
        operation: One of: summary, mean, median, sd, var, min, max, sum, quantile, fivenum
        
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


@server.tool()
async def r_lm_formula(
    formula: str,
    data: Dict[str, List[Any]]
) -> Dict[str, Any]:
    """
    Perform linear regression with formula
    
    Args:
        formula: R formula string (e.g., "y ~ x1 + x2")
        data: Dictionary of variables
        
    Returns:
        Regression results
    """
    return await call_r_api("/api/lm", {
        "formula": formula,
        "data": data
    })


@server.tool()
async def r_dataframe(
    data: Dict[str, List[Any]],
    operation: str = "summary"
) -> Dict[str, Any]:
    """
    Perform operations on data frames
    
    Args:
        data: Dictionary representing a data frame
        operation: One of: summary, dim, names, head, tail, str
        
    Returns:
        Operation result
    """
    return await call_r_api("/api/dataframe", {
        "data": data,
        "operation": operation
    })


# Specialized convenience functions

@server.tool()
async def r_correlation(
    x: List[float],
    y: List[float],
    method: str = "pearson"
) -> Dict[str, Any]:
    """
    Calculate correlation between two variables
    
    Args:
        x: First variable
        y: Second variable
        method: Correlation method (pearson, spearman, kendall)
        
    Returns:
        Correlation coefficient and test results
    """
    code = f"""
    x <- c({', '.join(map(str, x))})
    y <- c({', '.join(map(str, y))})
    cor.test(x, y, method = "{method}")
    """
    return await call_r_api("/api/execute", {"code": code})


@server.tool()
async def r_t_test(
    x: List[float],
    y: Optional[List[float]] = None,
    paired: bool = False,
    alternative: str = "two.sided"
) -> Dict[str, Any]:
    """
    Perform t-test
    
    Args:
        x: First sample
        y: Second sample (optional for one-sample test)
        paired: Whether to perform paired t-test
        alternative: One of: two.sided, less, greater
        
    Returns:
        T-test results
    """
    if y is None:
        code = f"""
        x <- c({', '.join(map(str, x))})
        t.test(x, alternative = "{alternative}")
        """
    else:
        code = f"""
        x <- c({', '.join(map(str, x))})
        y <- c({', '.join(map(str, y))})
        t.test(x, y, paired = {str(paired).upper()}, alternative = "{alternative}")
        """
    
    return await call_r_api("/api/execute", {"code": code})


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
    print(f"Make sure the R API server is running: Rscript base_r_api.R")
    
    server.run()


if __name__ == "__main__":
    main()