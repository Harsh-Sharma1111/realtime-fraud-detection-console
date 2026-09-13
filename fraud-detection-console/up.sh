#!/bin/bash
echo "Starting the fraud-detection-console stack..."
docker-compose up -d

echo ""
echo "Stack started in background."
echo "Use './logs.sh' to view logs or 'docker-compose ps' to check health status."
