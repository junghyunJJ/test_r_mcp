# R MCP Test Project

This project demonstrates how to create MCP (Model Context Protocol) servers using R, with two different approaches.

## Approaches

### 1. mcptools Approach (Recommended)
Uses the official `mcptools` package from Posit to create a native R MCP server.

**Files:**
- `hello_r_mcp_server.R`: MCP server with custom R functions
- `claude_desktop_config.json`: Configuration for Claude Desktop

**Setup:**
```bash
# Install mcptools
Rscript -e "pak::pak('posit-dev/mcptools')"

# Copy config to Claude Desktop
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop
```

**Usage in Claude Desktop:**
- "Run R code: `hello_r('Claude')`"
- "Run R code: `analyze_data(100)`"
- Execute any R code directly!

### 2. Python-R Bridge Approach (Legacy)
Uses FastMCP in Python to bridge HTTP requests to an R REST API.

**Files:**
- `hello_r_api.R` / `simple_r_api.R`: R REST API servers
- `hello_r_bridge.py`: Python MCP bridge server

**Setup:**
```bash
# Install R dependencies
Rscript -e "install.packages(c('RestRserve', 'jsonlite'))"

# Install Python dependencies
uv sync

# Start R API server
Rscript hello_r_api.R

# In another terminal, start Python MCP bridge
python hello_r_bridge.py
```

## Available Functions

### mcptools Server
- `hello_r(name)`: Returns greeting with R version info
- `analyze_data(n)`: Generates and analyzes sample data
- Direct R code execution

### Python-R Bridge
- `hello_r`: Say hello through R API
- `check_r_status`: Check R API server status

## Requirements

- R 4.0+
- Python 3.13+ (for bridge approach)
- mcptools package (for native approach)
- Claude Desktop (for testing)