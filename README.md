# R MCP Bridge

A clean, extensible bridge that exposes R functionality through the Model Context Protocol (MCP), allowing AI assistants like Claude to leverage R's powerful statistical and data analysis capabilities.

## Features

- 🔍 **Server Status** - Check if the R API is running and healthy
- 👋 **Greetings** - Simple interaction with R
- 🧮 **Basic Math** - Perform calculations using R
- 📊 **Statistical Operations** - Mean, median, SD, variance, min, max, sum
- 📈 **Linear Regression** - Simple linear regression analysis
- 🔬 **Extensible** - Easy to add new endpoints and functions

## Quick Start

### Prerequisites

- Python 3.10+
- R 4.0+
- R packages: `RestRserve`, `jsonlite`

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/r-mcp-bridge.git
cd r-mcp-bridge
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
# or with uv:
uv sync
```

3. Install R dependencies:
```R
install.packages(c("RestRserve", "jsonlite"))
```

### Running the Bridge

1. Start the R API server:
```bash
Rscript r_api.R
```

2. In a new terminal, start the MCP bridge:
```bash
python r_bridge.py
```

### Configure Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

**Option 1: Using Docker Hub (Easiest)**
```json
{
  "mcpServers": {
    "r-mcp": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "yourusername/r-mcp-bridge"]
    }
  }
}
```

**Option 2: Using Local Docker Build**
```json
{
  "mcpServers": {
    "r-mcp": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--pull", "always", "r-mcp-bridge:latest"]
    }
  }
}
```

**Option 3: Using uv (For Development)**
```json
{
  "mcpServers": {
    "r-mcp": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/r-mcp-bridge/",
        "run",
        "r_bridge.py"
      ]
    }
  }
}
```

**Option 4: Using Python directly**
```json
{
  "mcpServers": {
    "r-mcp": {
      "command": "python",
      "args": [
        "/path/to/r-mcp-bridge/r_bridge.py"
      ],
      "env": {}
    }
  }
}
```

Note: 
- Docker options require Docker Desktop to be running
- Use `--pull always` to ensure you have the latest version
- For development, use uv or Python options

## Available MCP Tools

### r_status
Check the status of the R API server:
```
Tool: r_status
Returns: Server status, version info, and health status
```

### r_hello
Send a greeting to R:
```
Tool: r_hello
Arguments:
  - name (optional): Name to greet (default: "World")
Returns: Greeting message from R
```

### r_add
Add two numbers using R:
```
Tool: r_add
Arguments:
  - a: First number (default: 0)
  - b: Second number (default: 0)
Returns: Sum of a and b
```

### r_stats
Perform statistical operations on data:
```
Tool: r_stats
Arguments:
  - data: List of numbers
  - operation: One of "mean", "median", "sd", "var", "min", "max", "sum" (default: "mean")
Returns: Statistical result
```

### r_lm_simple
Perform simple linear regression:
```
Tool: r_lm_simple
Arguments:
  - x: List of x values (independent variable)
  - y: List of y values (dependent variable)
Returns: Regression coefficients, R-squared, p-value, and more
```

## Example Usage in Claude

Once configured, you can ask Claude to:

- "Check if the R server is running"
- "Calculate the mean of [1, 2, 3, 4, 5] using R"
- "Perform a linear regression on x=[1,2,3,4,5] and y=[2,4,5,4,5]"
- "Add 42 and 17 using R"

## Adding New Functions

### 1. Add R API Endpoint

Edit `r_api.R` to add a new endpoint:

```r
app$add_post(
    path = "/api/your_function",
    FUN = function(request, response) {
        tryCatch({
            body <- parse_request_body(request)
            
            # Your R logic here
            result <- your_r_function(body$param1, body$param2)
            
            success_response(response, list(
                result = result
            ))
            
        }, error = function(e) {
            error_response(response, e$message)
        })
    }
)
```

### 2. Add MCP Tool

Edit `r_bridge.py` to expose the function:

```python
@server.tool()
async def r_your_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Your function description
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of return value
    """
    return await call_r_api("/api/your_function", {
        "param1": param1,
        "param2": param2
    })
```

## Environment Variables

- `R_API_PORT`: Port for R API server (default: 8081)
- `R_API_URL`: Full URL for R API (default: http://localhost:8081)

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌────────────┐
│ Claude Desktop  │────▶│  r_bridge.py │────▶│  r_api.R   │
│   (MCP Client)  │◀────│ (MCP Server) │◀────│(R REST API)│
└─────────────────┘     └──────────────┘     └────────────┘
```

## Troubleshooting

### R API server not running
Make sure the R server is running before starting the Python bridge:
```bash
Rscript r_api.R
```

### Port already in use
Change the port using environment variable:
```bash
R_API_PORT=8082 Rscript r_api.R
R_API_PORT=8082 python r_bridge.py
```

### Missing R packages
Install required packages:
```R
install.packages(c("RestRserve", "jsonlite"))
```

## Future Enhancements

The following features are planned for future releases:

- 🚀 **Execute arbitrary R code** - Run any R expression and get results
- 🧮 **Function calls** - Call any R function with arguments
- 📋 **Data frame operations** - Work with structured data
- 📊 **Advanced statistics** - Correlation, t-tests, ANOVA
- 📈 **Multiple regression** - Support for formula-based regression

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your endpoint to `r_api.R`
4. Add corresponding MCP tool to `r_bridge.py`
5. Update this README
6. Submit a pull request

## Docker Deployment

### Quick Start with Docker Hub

The easiest way to use R MCP Bridge is through Docker Hub:

```bash
# Pull and run directly (no installation needed!)
docker run -i --rm yourusername/r-mcp-bridge
```

That's it! No need to install R, Python, or any dependencies.

### Building Your Own Docker Image

```bash
# Clone the repository
git clone https://github.com/yourusername/r-mcp-bridge.git
cd r-mcp-bridge

# Build the Docker image
docker build -f Dockerfile.mcp -t r-mcp-bridge .

# Test locally
docker run -i --rm r-mcp-bridge
```

### Publishing to Docker Hub

Use the provided build script for multi-platform support:

```bash
# Build and push to Docker Hub
./build-docker-mcp.sh --push
```

### Docker Image Features

- **Optimized for MCP**: Designed specifically for Claude Desktop integration
- **Multi-platform**: Supports both Intel and ARM (M1/M2) Macs
- **Lightweight**: ~400-500MB (optimized from ~800MB)
- **Self-contained**: Includes both R and Python environments
- **Secure**: Runs as non-root user with minimal attack surface

See [DOCKER_HUB.md](DOCKER_HUB.md) for detailed Docker Hub deployment guide.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) for Python
- Uses [RestRserve](https://restrserve.org/) for R REST API
- Inspired by the Model Context Protocol specification