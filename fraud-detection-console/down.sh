#!/bin/bash
echo "Stopping the fraud-detection-console stack and preserving volumes..."
docker-compose down

# To completely wipe the database volume, you would use:
# docker-compose down -v
