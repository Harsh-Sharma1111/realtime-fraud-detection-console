# Fraud Detection Console

This is a real-time fraud detection pipeline with the following structure:

- `simulator/`: Python transaction generator
- `streaming/`: PySpark structured streaming job
- `backend/`: FastAPI REST + WebSocket server
- `frontend/`: React dashboard

## Prerequisites
- Docker & Docker Compose
- (Optional) Git Bash or WSL for running `.sh` scripts on Windows

## Services
- **Zookeeper**: Port 2181
- **Kafka**: Port 9092 (mapped to host for easy access)
- **MongoDB**: Port 27017
