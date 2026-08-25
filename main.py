import argparse
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from simulator.kafka_producer import BankingKafkaProducer
from simulator.transaction_generator import TransactionGenerator
from streaming.consumer_test import run_consumer
from config.settings import SIMULATOR_DEFAULT_RATE, FRAUD_INJECTION_RATE

def main():
    parser = argparse.ArgumentParser(description="Real-Time Fraud Detection Console - Phase 1 CLI Tool")
    parser.add_argument(
        "--mode",
        choices=["stream", "consume", "simulate", "seed"],
        default="stream",
        help="Execution mode: 'stream' (publish to Kafka), 'consume' (listen to Kafka stream), 'simulate' (console print), 'seed' (generate seed dataset)"
    )
    parser.add_argument("--rate", type=float, default=SIMULATOR_DEFAULT_RATE, help="Transactions per second to produce (default: 5)")
    parser.add_argument("--count", type=int, default=None, help="Number of transactions to generate/process (default: continuous)")
    parser.add_argument("--fraud-rate", type=float, default=FRAUD_INJECTION_RATE, help="Fraud injection probability (default: 0.08)")

    args = parser.parse_args()

    print("==========================================================================")
    print("      REAL-TIME FRAUD DETECTION CONSOLE - BIG DATA PIPELINE (PHASE 1)     ")
    print("==========================================================================")
    print(f" Mode: {args.mode.upper()} | Rate: {args.rate} msg/sec | Fraud Injection: {args.fraud_rate * 100:.1f}%\n")

    if args.mode == "stream":
        producer = BankingKafkaProducer()
        producer.start_streaming(rate=args.rate, count=args.count)

    elif args.mode == "consume":
        run_consumer(max_messages=args.count)

    elif args.mode == "simulate":
        gen = TransactionGenerator(fraud_rate=args.fraud_rate)
        count = args.count if args.count else 10
        print(f"[*] Simulating {count} transaction events to console:\n")
        fraud_count = 0
        for i, tx in enumerate(gen.stream_transactions(count=count), 1):
            if tx.is_fraud:
                fraud_count += 1
            print(
                f"[{i:02d}] TxID={tx.transaction_id} | Account={tx.account_id} | "
                f"Amount=${tx.amount:>8.2f} | Category={tx.category:<12} | "
                f"Fraud={tx.is_fraud} ({tx.fraud_type}) | City={tx.location.city}"
            )
        print(f"\n[SUMMARY] Generated {count} transactions. Fraud events: {fraud_count} ({(fraud_count/count*100):.1f}%)")

    elif args.mode == "seed":
        import pandas as pd
        os.makedirs("data", exist_ok=True)
        gen = TransactionGenerator(fraud_rate=args.fraud_rate)
        total = args.count if args.count else 1000
        print(f"[*] Generating synthetic seed dataset with {total} records for offline analytics/model calibration...")
        records = []
        for tx in gen.stream_transactions(count=total):
            d = tx.model_dump()
            # Flatten location
            d["latitude"] = tx.location.latitude
            d["longitude"] = tx.location.longitude
            d["city"] = tx.location.city
            d["country"] = tx.location.country
            del d["location"]
            records.append(d)
        
        df = pd.DataFrame(records)
        seed_path = os.path.join("data", "seed_transactions.csv")
        df.to_csv(seed_path, index=False)
        print(f"[OK] Seed dataset successfully saved to: {seed_path}")
        print(f"    Shape: {df.shape} | Fraud Count: {df['is_fraud'].sum()} ({(df['is_fraud'].sum()/len(df)*100):.1f}%)")

if __name__ == "__main__":
    main()
