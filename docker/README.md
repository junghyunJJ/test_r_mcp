# Docker Deployment Guide

This guide explains how to deploy the R MCP Bridge using Docker.

## Quick Start

### Build and run with Docker Compose (Recommended)

```bash
# Production deployment (single container)
docker-compose -f docker-compose.prod.yml up -d

# Development deployment (separate containers)
docker-compose up -d
```

### Build and run manually

```bash
# Build the image
docker build -t r-mcp-bridge .

# Run the container
docker run -d \
  -p 8080:8080 \
  -p 8081:8081 \
  --name r-mcp-bridge \
  r-mcp-bridge
```

## Image Variants

### 1. Standard Image (Debian-based)
- **File**: `Dockerfile`
- **Size**: ~400-500MB
- **Stability**: High
- **Use case**: Production deployments

### 2. Alpine Image (Experimental)
- **File**: `Dockerfile.alpine`
- **Size**: ~200-300MB
- **Stability**: May have compatibility issues
- **Use case**: When minimal size is critical

```bash
# Build Alpine variant
docker build -f Dockerfile.alpine -t r-mcp-bridge:alpine .
```

## Configuration

### Environment Variables

- `R_API_PORT`: R API server port (default: 8081)
- `R_API_URL`: R API server URL (default: http://localhost:8081)
- `MCP_PORT`: MCP server port (default: 8080)

### Docker Compose Options

1. **Production (Single Container)**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```
   - Both services in one container
   - Resource limits configured
   - Automatic restart
   - Log rotation

2. **Development (Separate Containers)**
   ```bash
   docker-compose up -d
   ```
   - R API and MCP bridge in separate containers
   - Easier debugging
   - Independent scaling

## Optimization Tips

### 1. Multi-stage Build
The Dockerfile uses multi-stage builds to minimize the final image size:
- Build stage: Compiles R packages and Python dependencies
- Runtime stage: Contains only necessary runtime files

### 2. Layer Caching
```bash
# Build with BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t r-mcp-bridge .
```

### 3. Slim Base Images
- Uses `python:3.11-slim` instead of full Python image
- Uses `r-base-core` for minimal R installation

### 4. Cleanup
- Removes package manager caches
- Removes documentation and man pages
- Removes build dependencies

## Health Checks

The container includes health checks for both services:

```bash
# Check container health
docker ps
docker inspect r-mcp-bridge --format='{{.State.Health.Status}}'

# View health check logs
docker inspect r-mcp-bridge --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs r-mcp-bridge

# Check if ports are already in use
lsof -i :8080
lsof -i :8081
```

### R packages installation fails
```bash
# Build with no cache
docker build --no-cache -t r-mcp-bridge .

# Or use a different CRAN mirror
docker build --build-arg CRAN_MIRROR=https://cran.rstudio.com/ -t r-mcp-bridge .
```

### Out of memory
Increase Docker memory limits or use production compose file with resource limits:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Security Considerations

1. **Non-root User**: Container runs as non-root user (uid 1000)
2. **Minimal Attack Surface**: Only necessary packages installed
3. **Network Isolation**: Use Docker networks for service communication
4. **Resource Limits**: Configure CPU and memory limits in production

## Monitoring

```bash
# View resource usage
docker stats r-mcp-bridge

# View logs
docker logs -f r-mcp-bridge

# Execute commands in container
docker exec -it r-mcp-bridge /bin/bash
```

## Claude Desktop Integration

### Using Docker with Claude Desktop

The R MCP Bridge can be used with Claude Desktop through Docker:

1. **Ensure Docker Desktop is running**

2. **Use the provided run script**:
   ```json
   {
     "mcpServers": {
       "r-mcp": {
         "command": "/path/to/r-mcp-bridge/run-docker-mcp.sh"
       }
     }
   }
   ```

   For Windows:
   ```json
   {
     "mcpServers": {
       "r-mcp": {
         "command": "C:\\path\\to\\r-mcp-bridge\\run-docker-mcp.bat"
       }
     }
   }
   ```

### How it works

1. The run script starts the R API server in a background container
2. It then runs the MCP bridge in stdio mode, connected to the R API
3. Claude Desktop communicates with the MCP bridge via stdio
4. When Claude Desktop stops, the containers are automatically cleaned up

### Advanced Configuration

You can customize the Docker execution by setting environment variables:

```json
{
  "mcpServers": {
    "r-mcp": {
      "command": "/path/to/r-mcp-bridge/run-docker-mcp.sh",
      "env": {
        "R_MCP_IMAGE": "r-mcp-bridge:custom",
        "R_API_PORT": "8082"
      }
    }
  }
}
```

### Troubleshooting Claude Desktop Integration

1. **"Docker is not running" error**
   - Make sure Docker Desktop is started before launching Claude Desktop

2. **Permission denied**
   - Make the run script executable: `chmod +x run-docker-mcp.sh`

3. **Container conflicts**
   - The script uses unique container names, but you can check for conflicts:
   ```bash
   docker ps -a | grep r-mcp-claude
   ```

4. **Debugging**
   - Check the Claude Desktop logs
   - Run the script manually to see error messages:
   ```bash
   ./run-docker-mcp.sh
   ```