"""
R MCP Bridge - A clean, extensible bridge between R and MCP (Refactored)
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, List, Union, Callable
from functools import wraps
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


# ============= Helper Functions =============

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


def format_r_vector(values: List[Any]) -> str:
    """Convert Python list to R vector string"""
    return f"c({', '.join(map(str, values))})"


def build_r_code(template: str, **kwargs) -> str:
    """Build R code from template with proper formatting"""
    # Convert lists to R vectors
    for key, value in kwargs.items():
        if isinstance(value, list):
            kwargs[key] = format_r_vector(value)
        elif isinstance(value, bool):
            kwargs[key] = str(value).upper()
        elif isinstance(value, str) and key not in ['method', 'alternative', 'formula']:
            kwargs[key] = f'"{value}"'
    
    return template.format(**kwargs)


def create_simple_r_tool(endpoint: str):
    """Decorator factory for simple R API tools"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Dict[str, Any]:
            # Build payload from function arguments
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            payload = dict(bound.arguments)
            
            return await call_r_api(endpoint, payload)
        
        # Register with MCP server
        return server.tool()(wrapper)
    
    return decorator


# ============= MCP Tools =============

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


@create_simple_r_tool("/api/execute")
async def r_execute(code: str) -> Dict[str, Any]:
    """
    Execute arbitrary R code
    
    Args:
        code: R code to execute
        
    Returns:
        Execution result and output
    """
    pass  # Implementation handled by decorator


@create_simple_r_tool("/api/call")
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
    pass  # Implementation handled by decorator


@create_simple_r_tool("/api/stats")
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
    pass  # Implementation handled by decorator


@create_simple_r_tool("/api/lm")
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
    pass  # Implementation handled by decorator


@create_simple_r_tool("/api/lm")
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
    pass  # Implementation handled by decorator


@create_simple_r_tool("/api/dataframe")
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
    pass  # Implementation handled by decorator


# ============= Specialized Functions =============

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
    code = build_r_code(
        """
        x <- {x}
        y <- {y}
        cor.test(x, y, method = "{method}")
        """,
        x=x, y=y, method=method
    )
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
        code = build_r_code(
            """
            x <- {x}
            t.test(x, alternative = "{alternative}")
            """,
            x=x, alternative=alternative
        )
    else:
        code = build_r_code(
            """
            x <- {x}
            y <- {y}
            t.test(x, y, paired = {paired}, alternative = "{alternative}")
            """,
            x=x, y=y, paired=paired, alternative=alternative
        )
    
    return await call_r_api("/api/execute", {"code": code})


@server.tool()
async def r_anova(
    formula: str,
    data: Dict[str, List[Any]]
) -> Dict[str, Any]:
    """
    Perform ANOVA (Analysis of Variance)
    
    Args:
        formula: R formula string (e.g., "response ~ factor")
        data: Dictionary of variables
        
    Returns:
        ANOVA table and results
    """
    code = build_r_code(
        """df <- data.frame({data_args})
model <- aov({formula}, data = df)
summary(model)""",
        data_args=", ".join(f"{k} = {format_r_vector(v)}" for k, v in data.items()),
        formula=formula
    )
    return await call_r_api("/api/execute", {"code": code})


@server.tool()
async def r_plot(
    x: List[float],
    y: Optional[List[float]] = None,
    plot_type: str = "scatter",
    title: str = "",
    xlab: str = "X",
    ylab: str = "Y"
) -> Dict[str, Any]:
    """
    Create basic plots (returns plot parameters, not image)
    
    Args:
        x: X values
        y: Y values (optional for histograms)
        plot_type: Type of plot (scatter, line, histogram, boxplot)
        title: Plot title
        xlab: X-axis label
        ylab: Y-axis label
        
    Returns:
        Plot parameters and summary statistics
    """
    if plot_type == "histogram" and y is None:
        code = build_r_code(
            """x <- {x}
hist_data <- hist(x, plot = FALSE)
list(
    breaks = hist_data$breaks,
    counts = hist_data$counts,
    density = hist_data$density,
    mids = hist_data$mids,
    summary = summary(x)
)""",
            x=x
        )
    elif plot_type == "boxplot":
        code = build_r_code(
            """x <- {x}
box_stats <- boxplot.stats(x)
list(
    stats = box_stats$stats,
    n = box_stats$n,
    conf = box_stats$conf,
    out = box_stats$out,
    summary = summary(x)
)""",
            x=x
        )
    else:
        # Scatter or line plot
        code = build_r_code(
            """x <- {x}
y <- {y}
list(
    x_range = range(x),
    y_range = range(y),
    x_summary = summary(x),
    y_summary = summary(y),
    correlation = cor(x, y)
)""",
            x=x, y=y or x
        )
    
    return await call_r_api("/api/execute", {"code": code})


# ============= Lifecycle Management =============

async def cleanup():
    """Cleanup resources on shutdown"""
    await http_client.aclose()


def main():
    """Run the MCP server"""
    import atexit
    atexit.register(lambda: asyncio.run(cleanup()))
    
    print(f"Starting R MCP Bridge Server (Refactored)...")
    print(f"Connecting to R API at: {R_API_BASE_URL}")
    print(f"Make sure the R API server is running: Rscript base_r_api.R")
    
    server.run()


if __name__ == "__main__":
    main()