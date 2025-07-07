#!/bin/bash
# Build script for Docker Hub MCP image

set -e

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-yourusername}"
IMAGE_NAME="${DOCKER_USERNAME}/r-mcp-bridge"
VERSION="${VERSION:-latest}"

echo "Building R MCP Bridge for Docker Hub..."
echo "Image: ${IMAGE_NAME}:${VERSION}"

# Ensure Docker Buildx is available
if ! docker buildx version > /dev/null 2>&1; then
    echo "Error: Docker Buildx is required for multi-platform builds"
    echo "Please update Docker Desktop or install buildx"
    exit 1
fi

# Create builder if it doesn't exist
if ! docker buildx ls | grep -q mcp-builder; then
    echo "Creating buildx builder..."
    docker buildx create --name mcp-builder --driver docker-container --bootstrap
fi

# Use the builder
docker buildx use mcp-builder

# Build options
BUILD_ARGS=""
if [ "$1" == "--push" ]; then
    BUILD_ARGS="--push"
    echo "Will push to Docker Hub after building"
else
    BUILD_ARGS="--load"
    echo "Building locally only (use --push to publish)"
fi

# Build the image
echo "Building multi-platform image..."
docker buildx build \
    -f Dockerfile.mcp \
    --platform linux/amd64,linux/arm64 \
    -t "${IMAGE_NAME}:${VERSION}" \
    -t "${IMAGE_NAME}:latest" \
    --cache-from "type=registry,ref=${IMAGE_NAME}:buildcache" \
    --cache-to "type=registry,ref=${IMAGE_NAME}:buildcache,mode=max" \
    ${BUILD_ARGS} \
    .

echo "Build complete!"

if [ "$1" != "--push" ]; then
    echo ""
    echo "To test locally:"
    echo "  docker run -i --rm ${IMAGE_NAME}:${VERSION}"
    echo ""
    echo "To push to Docker Hub:"
    echo "  $0 --push"
fi