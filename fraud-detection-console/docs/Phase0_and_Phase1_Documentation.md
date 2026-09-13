# Real-Time Fraud Detection Console: Phase 0 & Phase 1 Documentation

This document serves as a comprehensive guide to the foundational infrastructure (Phase 0) and the Transaction Data Simulator (Phase 1) for the Real-Time Fraud Detection project.

---

## Phase 0: Foundational Infrastructure

### 1. Architecture Overview
Phase 0 established the core data infrastructure required to support a high-throughput streaming pipeline. The infrastructure is entirely containerized using Docker Compose.

**Services Deployed:**
- **Zookeeper (Port 2181):** Coordinates and manages the Kafka cluster state.
- **Kafka Broker (Port 9092):** The central message queue. It receives the stream of transactions from our Python simulator and holds them for our PySpark streaming job to process later. It is exposed to the host machine on `localhost:9092`.
- **MongoDB (Port 27017):** A NoSQL database with a persistent volume (`mongodb_data`) to store the final processed alerts and dashboards later in the project.

### 2. File Structure Established
- `docker-compose.yml`: Defines the Docker services, networking, and health checks.
- `simulator/`: Directory for the Python data generator.
- `streaming/`: Reserved for the PySpark streaming job (Phase 2).
- `backend/`: Reserved for the FastAPI server.
- `frontend/`: Reserved for the React dashboard.

### 3. Workflow & Terminal Commands

We created three helper shell scripts to easily manage the Docker environment.

**Start the Infrastructure:**
```bash
# Navigate to the project root
cd fraud-detection-console
# Run the startup script (spins up containers in the background)
./up.sh
```

**Monitor Logs:**
```bash
# Tail the logs of all running services
./logs.sh
```

**Stop the Infrastructure:**
```bash
# Stops the containers safely without destroying the database volume
./down.sh
```

**Verify Service Health Manually:**
*Check if containers are healthy:*
```bash
docker-compose ps
```
*Verify Kafka is actively running and can list topics:*
```bash
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```
*Verify MongoDB is accepting connections:*
```bash
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

---

## Phase 1: Transaction Simulator

### 1. Overview
The simulator (`simulator/generate_transactions.py`) acts as the "source" of our real-time data. It uses the `Faker` library to generate highly realistic, synthetic credit card transactions. 

### 2. Important Functions & Operations

#### `Initialization Logic`
When the script starts, it pre-computes a pool of 200 "dummy cards". For each card, it statically assigns:
- A unique 16-digit card number.
- A baseline spending amount (their typical transaction size).
- 1 or 2 "home cities" representing where they actually live/work.

This ensures that normal transactions follow a highly predictable and realistic geographical and financial pattern.

#### `generate_transaction(fraud_pct)`
This is the core engine of the script. It randomly selects a card from the pool and decides whether the transaction should be normal or fraudulent based on the defined `fraud_pct`.

**Normal Operation Branch:**
- **Amount:** Pulled from a log-normal distribution centered tightly around the card's baseline spend.
- **Location:** Strictly picked from the card's pre-assigned "home cities".
- **Timestamp:** Current real-time clock.

**Fraud Injection Branch:**
If the transaction triggers the fraud branch, it injects four anomalies simultaneously to simulate a stolen card:
1. **Amount Anomaly (High Velocity):** The amount is suddenly multiplied by 5x to 20x the card's baseline.
2. **Geographical Anomaly (Impossible Travel):** The location is forced to a completely random new country, breaking the "home city" rule.
3. **Temporal Anomaly (Odd-Hours):** The timestamp is overridden to trigger between 2 AM and 5 AM.
4. **Merchant Category Anomaly:** The transaction targets easily resalable goods or untraceable services (e.g., `electronics`, `gambling`, `travel`).

*Note: The simulator attaches a hidden boolean flag `_is_seeded_fraud` to the JSON payload. This is used strictly for grading precision/recall later and should not be used as a feature for the actual detection model.*

### 3. Workflow & Terminal Commands

**Setup Environment:**
```bash
# Navigate to the simulator directory
cd simulator

# Install the required Python packages (Faker and kafka-python-ng)
pip install -r requirements.txt
```

**Run the Simulator:**
```bash
# Run with default settings (5% fraud, 200ms delay)
python generate_transactions.py

# Run with custom arguments (e.g., 10% fraud, 100ms delay, stop after 60 seconds)
python generate_transactions.py --fraud-pct 10.0 --rate 100 --duration 60
```

**Verify Kafka Ingestion:**
To prove that the Python simulator is successfully pushing JSON data into Kafka, you can open a second terminal and run a Kafka Console Consumer:
```bash
# Run this from the project root (fraud-detection-console)
docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic transactions-topic --from-beginning --max-messages 5
```
