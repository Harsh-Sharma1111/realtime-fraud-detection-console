# Phase 1 Documentation: Infrastructure & Real-Time Data Simulation Layer

## Executive Summary
This document provides a comprehensive guide to **Phase 1** of the **Real-Time Fraud Detection Console** project for Big Data Analytics. 

In this phase, we established:
1. The **distributed streaming infrastructure** setup (`docker/docker-compose.yml`).
2. The **realistic synthetic banking transaction simulator** (`simulator/transaction_generator.py`).
3. The **4-pattern real-world fraud injection engine** (`simulator/fraud_injector.py`).
4. The **Apache Kafka publish-subscribe message producer** (`simulator/kafka_producer.py`) with fallback stream buffer support.
5. The **stream verification consumer tool** (`streaming/consumer_test.py`).
6. The **offline calibration seed dataset generator** (`data/seed_transactions.csv`).

---

## 1. Big Data Concepts & Architectural Foundations

### 1.1 The 3 V's in Financial Stream Ingestion
- **Volume**: Banks process millions of payments daily across credit cards, wire transfers, and digital wallets.
- **Velocity**: Transactions must be ingested, scored against fraud rules, and persisted in sub-second latency windows (milliseconds) before card approval or decline.
- **Variety**: Combining structured fields (amount, timestamps, merchant IDs) with geospatial coordinates (`lat`, `lon`, `city`), network identifiers (`IP`, `device_id`), and historical account behavior.

### 1.2 Pub-Sub Ingestion Architecture with Apache Kafka
Traditional request-response architectures collapse under traffic spikes. **Apache Kafka** decouples data producers (POS machines, online checkout portals, mobile apps) from stream consumers (Spark Structured Streaming engines, NoSQL stores, monitoring dashboards).

```
 +------------------------+        +--------------------------+        +------------------------+
 | Transaction Simulator  | -----> |   Apache Kafka Broker    | -----> |   Spark / Consumer     |
 | (Banking Producer)     |        | Topic: banking-txns      |        |   Verification Engine  |
 +------------------------+        +--------------------------+        +------------------------+
```

Key Benefits of Kafka in this Pipeline:
- **Durable Buffering**: Offsets and stores incoming events sequentially.
- **High Throughput**: Can ingest hundreds of thousands of messages per second with minimal latency.
- **Fault Tolerance & Scalability**: Partitioned log architecture allows horizontal scaling across consumer groups.

---

## 2. Component Walkthrough & Data Schema

### 2.1 Transaction Payload Schema
Each ingested event is formatted as a JSON record containing:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `transaction_id` | String | Unique UUID identifier (e.g., `TXN-932769117BD9`) |
| `account_id` | String | Customer account reference (e.g., `ACC-100042`) |
| `card_number` | String | Masked credit card number |
| `timestamp` | String | ISO-8601 UTC timestamp |
| `amount` | Float | Transaction amount in USD |
| `merchant_id` | String | Merchant entity ID |
| `merchant_name` | String | Business name and category |
| `category` | String | Merchant domain (Retail, Grocery, Gambling, Crypto, etc.) |
| `location` | Object | `{ latitude, longitude, city, country }` |
| `device_id` | String | Device hardware fingerprint |
| `ip_address` | String | Network IP address |
| `distance_from_home_km` | Float | Calculated Haversine distance from home city |
| `is_fraud` | Integer | Ground truth flag: `0` (Normal), `1` (Fraudulent) |
| `fraud_type` | String | Pattern classification (`NORMAL`, `HIGH_AMOUNT`, `IMPOSSIBLE_VELOCITY`, `ODD_HOURS`, `HIGH_RISK_MERCHANT`) |

---

### 2.2 Fraud Pattern Simulation Engine

To reflect realistic banking fraud vectors, the simulator embeds a controlled percentage of anomalies (configurable, default `8.0%`):

1. **HIGH_AMOUNT**: Anomalous purchase spike ($2,500 - $9,500) significantly higher than the account's baseline standard deviation.
2. **IMPOSSIBLE_VELOCITY**: Geospatial anomaly where consecutive transactions occur in cities separated by thousands of kilometers within minutes (e.g., New York then Los Angeles), yielding impossible travel speed (> 800 km/h). Calculated using the **Haversine Formula**:
   $$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
3. **ODD_HOURS**: Burst of high-value transactions forced between 01:00 AM and 04:00 AM local time.
4. **HIGH_RISK_MERCHANT**: Sudden high-value transactions at high-risk merchant categories (`Gambling`, `Crypto`, `Luxury`) for accounts with dormant or low-risk historical profiles.

---

## 3. Containerized Infrastructure (`docker/docker-compose.yml`)

The multi-container stack runs via Docker Compose:

| Service | Port Mapping | Purpose |
| :--- | :--- | :--- |
| **Zookeeper** | `2181:2181` | Manages Kafka cluster state, leader elections, and topic metadata |
| **Kafka Broker** | `9092` (Int), `9094` (Host) | Ingestion message broker holding transaction stream |
| **MongoDB** | `27017:27017` | Hot storage NoSQL store for sub-second alert lookups and live console feed |
| **Spark Master** | `8080` (UI), `7077` (RPC) | Distributed cluster coordinator for real-time Spark Structured Streaming |
| **Spark Worker** | `8081` (UI) | Computes micro-batches and scores incoming Kafka stream |

---

## 4. How to Run Phase 1

### 4.1 Running Unit Tests
Execute the unit test suite to verify data schemas, distance math, profile creation, and fraud injection logic:
```bash
python -m unittest tests/test_simulator.py
```

### 4.2 Simulating & Producing the Live Ingestion Stream
Start the live transaction producer (streams 5 msgs/sec by default):
```bash
python main.py --mode stream --rate 5 --count 100
```
*Note: If Docker/Kafka is active, events are published directly to the Kafka broker. If running standalone, events are logged to the console and stored in `data/simulated_stream.jsonl` fallback log.*

### 4.3 Consuming & Verifying the Stream
Launch the real-time stream consumer verifier:
```bash
python main.py --mode consume
```

### 4.4 Generating Offline Calibration Seed Dataset
Create a 1,000-record CSV dataset for baseline statistical calibration and offline ML model training:
```bash
python main.py --mode seed --count 1000
```

---

## 5. Summary & Next Steps for Phase 2
Phase 1 successfully establishes the streaming producer, fraud injector engine, Kafka broker ingestion pipeline, seed dataset, and verification suite. 

In **Phase 2**, we will implement **Apache Spark Structured Streaming** to read micro-batches from Kafka in real time, apply stateful window aggregations, calculate dynamic fraud risk scores, and flag suspicious transactions instantly.
