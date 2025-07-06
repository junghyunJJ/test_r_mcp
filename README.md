# R MCP Bridge

A clean, extensible bridge that exposes R functionality through the Model Context Protocol (MCP), allowing AI assistants like Claude to leverage R's powerful statistical and data analysis capabilities.

## Features

- 🚀 **Execute arbitrary R code** - Run any R expression and get results
- 📊 **Statistical operations** - Mean, median, SD, variance, quantiles, and more
- 📈 **Linear regression** - Simple and multiple regression with formula support
- 🧮 **Function calls** - Call any R function with arguments
- 📋 **Data frame operations** - Work with structured data
- 🔬 **Extensible** - Easy to add new endpoints and functions

## Quick Start

### Prerequisites

- Python 3.8+
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
Rscript base_r_api.R
```

2. In a new terminal, start the MCP bridge:
```bash
python r_bridge.py
```

### Configure Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "r-bridge": {
      "command": "python",
      "args": [
        "/path/to/r-mcp-bridge/r_bridge.py"
      ],
      "env": {}
    }
  }
}
```

## Available MCP Tools

### r_execute
Execute arbitrary R code:
```python
result = await r_execute("mean(c(1,2,3,4,5))")
```

### r_call
Call R functions with arguments:
```python
result = await r_call("rnorm", {"n": 10, "mean": 0, "sd": 1})
```

### r_stats
Perform statistical operations:
```python
result = await r_stats([1, 2, 3, 4, 5], operation="summary")
```

### r_lm_simple
Simple linear regression:
```python
result = await r_lm_simple(
    x=[1, 2, 3, 4, 5],
    y=[2, 4, 5, 4, 5]
)
```

### r_lm_formula
Multiple regression with formula:
```python
result = await r_lm_formula(
    formula="mpg ~ cyl + disp + hp",
    data={
        "mpg": [21.0, 21.0, 22.8, ...],
        "cyl": [6, 6, 4, ...],
        "disp": [160, 160, 108, ...],
        "hp": [110, 110, 93, ...]
    }
)
```

### r_dataframe
Data frame operations:
```python
result = await r_dataframe(
    data={"x": [1, 2, 3], "y": [4, 5, 6]},
    operation="summary"
)
```

### r_correlation
Calculate correlation:
```python
result = await r_correlation(
    x=[1, 2, 3, 4, 5],
    y=[2, 4, 5, 4, 5],
    method="pearson"
)
```

### r_t_test
Perform t-tests:
```python
# One-sample t-test
result = await r_t_test([1, 2, 3, 4, 5])

# Two-sample t-test
result = await r_t_test(
    x=[1, 2, 3, 4, 5],
    y=[2, 3, 4, 5, 6],
    paired=False
)
```

## Adding New Functions

### 1. Add R API Endpoint

Edit `base_r_api.R` to add a new endpoint:

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
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│ Claude Desktop  │────▶│  r_bridge.py │────▶│ base_r_api.R│
│   (MCP Client)  │◀────│ (MCP Server) │◀────│ (R REST API)│
└─────────────────┘     └──────────────┘     └─────────────┘
```

## Troubleshooting

### R API server not running
Make sure the R server is running before starting the Python bridge:
```bash
Rscript base_r_api.R
```

### Port already in use
Change the port using environment variable:
```bash
R_API_PORT=8082 Rscript base_r_api.R
R_API_PORT=8082 python r_bridge.py
```

### Missing R packages
Install required packages:
```R
install.packages(c("RestRserve", "jsonlite"))
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your endpoint to `base_r_api.R`
4. Add corresponding MCP tool to `r_bridge.py`
5. Update this README
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) for Python
- Uses [RestRserve](https://restrserve.org/) for R REST API
- Inspired by the Model Context Protocol specification