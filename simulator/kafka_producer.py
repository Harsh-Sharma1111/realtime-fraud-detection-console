import json
import time
import os
from typing import Optional
from kafka import KafkaProducer
from simulator.transaction_generator import TransactionGenerator
from config.settings import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_TRANSACTIONS, SIMULATOR_DEFAULT_RATE

class BankingKafkaProducer:
    def __init__(self, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, topic=KAFKA_TOPIC_TRANSACTIONS):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: Optional[KafkaProducer] = None
        self.is_connected = False
        self._connect_kafka()

    def _connect_kafka(self):
        print(f"[*] Attempting connection to Kafka brokers at: {self.bootstrap_servers}")
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8'),
                request_timeout_ms=3000,
                max_block_ms=3000
            )
            self.is_connected = True
            print(f"[OK] Connected to Kafka Broker successfully! Target topic: '{self.topic}'")
        except Exception as e:
            self.is_connected = False
            print(f"[!] Kafka Broker unavailable ({e}). Operating in Local Stream Buffer mode.")

    def start_streaming(self, rate: float = SIMULATOR_DEFAULT_RATE, count: int = None):
        generator = TransactionGenerator()
        interval = 1.0 / rate if rate > 0 else 0.1
        total_sent = 0
        fraud_sent = 0

        print(f"\n[>>>] Starting live streaming pipeline at {rate} msg/sec...")
        try:
            for tx in generator.stream_transactions(count=count):
                payload = tx.model_dump()
                key = tx.account_id

                if self.is_connected and self.producer:
                    self.producer.send(self.topic, key=key, value=payload)
                    self.producer.flush()
                else:
                    # Fallback buffer log
                    os.makedirs("data", exist_ok=True)
                    with open("data/simulated_stream.jsonl", "a") as f:
                        f.write(json.dumps(payload) + "\n")

                total_sent += 1
                if tx.is_fraud:
                    fraud_sent += 1

                print(
                    f"[{'ALERT' if tx.is_fraud else 'INFO'}] TxID={tx.transaction_id} | "
                    f"Card={tx.card_number[:6]}... | Amt=${tx.amount:,.2f} | "
                    f"Cat={tx.category:<12} | Fraud={tx.is_fraud} ({tx.fraud_type})"
                )

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[!] Stream interrupted by user.")
        finally:
            if self.producer:
                self.producer.close()
            print(f"\n[SUMMARY] Streaming Finished. Total Sent: {total_sent} | Fraud Events: {fraud_sent} ({(fraud_sent/total_sent*100) if total_sent > 0 else 0:.1f}%)")
