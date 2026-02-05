#!/bin/bash
set -e

VERSION=${1:-latest}
IMAGE="ghcr.io/boxlite-ai/claudebox-runtime"

echo "Building $IMAGE:$VERSION..."
docker build -t "$IMAGE:$VERSION" .

if [ "$VERSION" != "latest" ]; then
    docker tag "$IMAGE:$VERSION" "$IMAGE:latest"
    echo "Also tagged: $IMAGE:latest"
fi

echo "Done: $IMAGE:$VERSION"
