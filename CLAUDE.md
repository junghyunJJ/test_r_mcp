# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

R MCP Bridge - A Model Context Protocol server that exposes R's statistical and data analysis capabilities to AI assistants through a two-tier architecture:
- **R API Server** (`r_api.R`): RestRserve-based REST API running on port 8081
- **Python MCP Bridge** (`r_bridge.py`): FastMCP server that communicates with R via HTTP

## Development Commands

### Running the Application

1. **Start R API Server** (required first):
```bash
Rscript r_api.R
# Or with custom port: R_API_PORT=8082 Rscript r_api.R
```

2. **Start MCP Bridge**:
```bash
# Using Python directly
python r_bridge.py

# Using uv (recommended for development)
uv sync  # Install dependencies
uv run r_bridge.py

# With custom R API port
R_API_PORT=8082 python r_bridge.py
```

### Code Quality

```bash
# Format code with Black
black r_bridge.py

# Lint with Ruff
ruff check r_bridge.py

# Install development dependencies
pip install -e ".[dev]"
# or with uv:
uv sync --all-extras
```

### Docker Operations

```bash
# Build Docker image
docker build -f Dockerfile.mcp -t r-mcp-bridge .

# Build multi-platform with push to Docker Hub
./build-docker-mcp.sh --push

# Test Docker image locally
docker run -i --rm r-mcp-bridge
```

## Architecture & Key Components

### Core Files
- **`r_api.R`**: R REST API server with endpoints for statistics, regression, and basic operations
- **`r_bridge.py`**: Python MCP server that proxies requests to R API
- **`entrypoint.sh`**: Docker orchestration script that manages both services

### Available MCP Tools
- `r_status`: Check R API health
- `r_hello`: Test connectivity with optional name parameter
- `r_add`: Basic arithmetic (a + b)
- `r_stats`: Statistical operations (mean, median, sd, var, min, max, sum)
- `r_lm_simple`: Simple linear regression with detailed output

### Adding New Functions

1. **Add R endpoint in `r_api.R`**:
```r
app$add_post(
    path = "/api/your_function",
    FUN = function(request, response) {
        tryCatch({
            body <- parse_request_body(request)
            result <- your_r_function(body$param)
            success_response(response, list(result = result))
        }, error = function(e) {
            error_response(response, e$message)
        })
    }
)
```

2. **Add MCP tool in `r_bridge.py`**:
```python
@server.tool()
async def r_your_function(param: str) -> Dict[str, Any]:
    """Your function description"""
    return await call_r_api("/api/your_function", {"param": param})
```

## Important Notes

- **No test suite exists** - Consider adding pytest tests when implementing new features
- **R dependencies**: RestRserve, jsonlite, Rserve (install with `install.packages()`)
- **Python 3.10+** required, with 3.13 as current development version
- **Docker image** is optimized for stdio-based MCP communication
- **Environment variables**: `R_API_PORT` (default: 8081), `R_API_URL` (default: http://localhost:8081)