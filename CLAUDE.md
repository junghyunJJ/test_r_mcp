# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-R bridge project that uses the Model Context Protocol (MCP) to expose R functionality through Python. It demonstrates how to create REST APIs in R and bridge them to MCP-compatible tools.

## Commands

### Starting the R API Server
```bash
Rscript hello_r_api.R
```
The R server runs on port 8081 and provides `/health` and `/api/hello` endpoints.

### Running the Python MCP Bridge
```bash
python hello_r_bridge.py
```
This starts the MCP server that bridges Python to the R API.

### Managing Dependencies
```bash
# Install Python dependencies using uv
uv sync

# Install R dependencies
Rscript -e "install.packages(c('RestRserve', 'jsonlite'))"
```

## Architecture

The project follows a three-tier architecture:

1. **R API Layer** (`hello_r_api.R`): RestRserve-based REST API that exposes R functionality
2. **Python Bridge Layer** (`hello_r_bridge.py`): FastMCP server that translates between MCP protocol and HTTP requests to the R API
3. **MCP Client Layer**: Any MCP-compatible client can interact with the exposed tools

### Key Components

- **hello_r_bridge.py**: Main MCP server implementation
  - Exposes two MCP tools: `hello_r` and `check_r_status`
  - Uses httpx for async HTTP communication with R server
  - Handles error states when R server is offline

- **hello_r_api.R**: R REST API server
  - Uses RestRserve framework
  - Provides JSON responses with R version information
  - Includes error handling for malformed requests

## Development Notes

- The project uses Python 3.13+ and modern async patterns
- R API server must be running before the Python MCP bridge can function
- The bridge includes health checks to verify R server availability
- All API responses are JSON-formatted for consistency