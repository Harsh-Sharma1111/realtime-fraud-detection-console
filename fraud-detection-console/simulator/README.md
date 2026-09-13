# Transaction Simulator

This component is responsible for generating a continuous stream of synthetic, realistic credit card transactions and publishing them to a Kafka topic.

## Overview
The simulator uses the `Faker` library to generate highly realistic data. At startup, it pre-computes a pool of 200 "dummy cards." Each card is assigned:
- A unique 16-digit card number.
- A baseline spending amount (their typical budget).
- 1 to 2 "home cities" representing their normal geographical bounds.

## Transaction Schema
Each transaction published to Kafka is a JSON object shaped like this:
```json
{
  "transaction_id": "b4dc3165-b94a-4314-bb35-79e3f899859c", 
  "card_id": "180058075712018", 
  "amount": 54.8, 
  "merchant": "Sampson-Skinner", 
  "merchant_category": "healthcare", 
  "location": "Joelchester, Faroe Islands", 
  "timestamp": "2026-09-13T14:32:11.339503", 
  "_is_seeded_fraud": false
}
```

## Fraud Injection Patterns
By default, 5% of transactions are randomly selected to be fraudulent. When a transaction is flagged as fraud, the simulator intentionally breaks the card's normal behavior profile by injecting three anomalies simultaneously:

1. **Amount Anomaly (High Velocity/Volume)**: The transaction amount is randomly multiplied by 5x to 20x the card's normal baseline.
2. **Geographical Anomaly (Impossible Travel)**: The location is forced to be a completely random city/country, defying the card's restricted "home cities" bounds.
3. **Temporal Anomaly (Odd-Hours)**: The timestamp is explicitly overridden to occur between 2 AM and 5 AM.
4. **Targeted Categories**: The merchant category is forced into high-risk categories like `electronics`, `gambling`, or `travel`.

*Note: The `_is_seeded_fraud` flag is injected purely for offline evaluation and grading (precision/recall). It should NOT be exposed as a feature to the scoring engine!*

## Running the Simulator

### Prerequisites
Make sure your Kafka broker (from Phase 0) is running and accessible on `localhost:9092`.

### Setup
```bash
cd simulator
pip install -r requirements.txt
```

### Usage
Run the script with default settings (5% fraud, 1 transaction every ~200ms):
```bash
python generate_transactions.py
```

Override default parameters using command-line arguments:
```bash
python generate_transactions.py --fraud-pct 10.0 --rate 100 --duration 60
```
- `--fraud-pct`: Percentage of transactions to inject fraud into (0.0 to 100.0).
- `--rate`: Base wait time in milliseconds between transactions (randomized slightly on each loop).
- `--duration`: Run the simulation for exactly N seconds and then cleanly exit.
