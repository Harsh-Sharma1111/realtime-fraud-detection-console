import json
import time
import os
import sys

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kafka import KafkaConsumer
from config.settings import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_TRANSACTIONS

def run_consumer(topic=KAFKA_TOPIC_TRANSACTIONS, max_messages=None):
    print(f"[*] Connecting Kafka Consumer to brokers: {KAFKA_BOOTSTRAP_SERVERS} | Topic: '{topic}'...")
    consumer = None
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='fraud-verifier-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=5000
        )
        print("[OK] Kafka Consumer connected! Listening for incoming live stream messages...\n")
        
        count = 0
        fraud_count = 0
        for message in consumer:
            tx = message.value
            count += 1
            if tx.get("is_fraud") == 1:
                fraud_count += 1
            
            print(
                f"[RECV #{count:03d}] TxID={tx.get('transaction_id')} | "
                f"Amount=${tx.get('amount'):,.2f} | Merchant={tx.get('merchant_name')} | "
                f"Fraud={tx.get('is_fraud')} ({tx.get('fraud_type')})"
            )
            
            if max_messages and count >= max_messages:
                break
                
        print(f"\n[SUMMARY] Consumer finished. Received: {count} messages | Flagged Fraud: {fraud_count}")
    except Exception as e:
        print(f"[!] Kafka Consumer error or broker offline ({e}). Checking local fallback stream file...")
        fallback_file = os.path.join("data", "simulated_stream.jsonl")
        if os.path.exists(fallback_file):
            with open(fallback_file, "r") as f:
                lines = f.readlines()
            print(f"[OK] Read {len(lines)} messages from local fallback file ({fallback_file}):")
            fraud_count = 0
            for idx, line in enumerate(lines[-20:], 1):  # print last 20
                tx = json.loads(line.strip())
                if tx.get("is_fraud") == 1:
                    fraud_count += 1
                print(f"[FILE #{idx:02d}] TxID={tx.get('transaction_id')} | Amt=${tx.get('amount'):,.2f} | Fraud={tx.get('is_fraud')} ({tx.get('fraud_type')})")
        else:
            print(f"[!] No fallback stream file found at {fallback_file}. Run the producer first!")
    finally:
        if consumer:
            consumer.close()

if __name__ == "__main__":
    run_consumer()
