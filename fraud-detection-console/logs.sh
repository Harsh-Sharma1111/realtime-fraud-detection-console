#!/bin/bash
echo "Tailing logs for all services (Press Ctrl+C to exit)..."
docker-compose logs -f
