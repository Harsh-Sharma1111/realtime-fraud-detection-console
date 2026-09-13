import argparse
import json
import logging
import random
import time
import uuid
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer

# Configuration
NUM_CARDS = 200
MERCHANT_CATEGORIES = [
    'grocery', 'electronics', 'travel', 'gambling', 
    'utilities', 'entertainment', 'restaurant', 'healthcare'
]

print("Initializing simulation data (generating fake cards and home locations)...")
fake = Faker()

# Generate a fixed pool of cards so we can simulate recurring behaviour
cards = []
for _ in range(NUM_CARDS):
    # Each card has 1 or 2 "home cities" representing their normal geographical bounds
    home_cities = [(fake.city(), fake.country()) for _ in range(random.randint(1, 2))]
    # Each card has a different normal spending profile
    base_amount = random.uniform(10, 100) 
    
    cards.append({
        'card_id': fake.credit_card_number(card_type=None),
        'home_cities': home_cities,
        'base_amount': base_amount
    })

def generate_transaction(fraud_pct: float):
    """
    Generates a single synthetic transaction.
    """
    card = random.choice(cards)
    is_fraud = random.random() < (fraud_pct / 100.0)
    now = datetime.now()
    
    if not is_fraud:
        # --- NORMAL BEHAVIOUR ---
        # 1. Amount: Log-normal distribution centered around the card's typical spend
        amount = random.lognormvariate(mu=0, sigma=0.5) * card['base_amount']
        amount = max(1.0, min(amount, card['base_amount'] * 4)) # Cap extreme outliers
        
        # 2. Location: Pick from the card's pre-assigned home cities
        city, country = random.choice(card['home_cities'])
        
        # 3. Time: Current timestamp
        timestamp = now.isoformat()
        merchant_category = random.choice(MERCHANT_CATEGORIES)
        
    else:
        # --- FRAUD BEHAVIOUR ---
        # 1. Amount: Sudden high amount (5x to 20x their normal base amount)
        amount = card['base_amount'] * random.uniform(5, 20)
        
        # 2. Location: "Impossible travel" - entirely random new location 
        city, country = fake.city(), fake.country()
        
        # 3. Time: Odd-hour timestamp (2 AM to 5 AM)
        odd_hour = random.randint(2, 5)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        fraud_time = now.replace(hour=odd_hour, minute=minute, second=second)
        timestamp = fraud_time.isoformat()
        
        # 4. Merchant Category: Fraudsters often target easily resalable goods or untraceable services
        merchant_category = random.choice(['electronics', 'gambling', 'travel'])
        
    merchant_name = fake.company()
    
    tx = {
        "transaction_id": str(uuid.uuid4()),
        "card_id": card["card_id"],
        "amount": round(amount, 2),
        "merchant": merchant_name,
        "merchant_category": merchant_category,
        "location": f"{city}, {country}",
        "timestamp": timestamp,
        "_is_seeded_fraud": is_fraud  # Hidden flag for offline evaluation
    }
    
    return tx

def main():
    parser = argparse.ArgumentParser(description="Transaction Simulator")
    parser.add_argument('--rate', type=int, default=200, help="Base milliseconds between transactions")
    parser.add_argument('--fraud-pct', type=float, default=5.0, help="Percentage of fraud to inject")
    parser.add_argument('--duration', type=int, default=0, help="Run for N seconds then stop (0 = forever)")
    args = parser.parse_args()

    start_time = time.time()
    topic = 'transactions-topic'
    
    print(f"Connecting to Kafka on localhost:9092...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Successfully connected to Kafka.")
    except Exception as e:
        print(f"Failed to connect to Kafka. Is it running? Error: {e}")
        return

    print(f"Starting simulation. Fraud rate: {args.fraud_pct}%, Base rate: {args.rate}ms")
    print("-" * 60)
    
    try:
        while True:
            if args.duration > 0 and (time.time() - start_time) > args.duration:
                print(f"\nReached {args.duration} seconds duration limit. Stopping.")
                break
                
            tx = generate_transaction(args.fraud_pct)
            
            # Publish to Kafka
            producer.send(topic, tx)
            
            # Print short console log
            fraud_marker = "\033[91m[FRAUD]\033[0m" if tx['_is_seeded_fraud'] else "\033[92m[ OK  ]\033[0m"
            card_last4 = tx['card_id'][-4:]
            print(f"{fraud_marker} TX: {tx['transaction_id'][:8]} | Card: ****{card_last4} | Amt: ${tx['amount']:7.2f} | Loc: {tx['location']}")
            
            # Add some jitter to the rate (e.g. rate to rate + 300ms)
            sleep_ms = random.randint(args.rate, args.rate + 300)
            time.sleep(sleep_ms / 1000.0)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
    finally:
        producer.flush()
        producer.close()
        print("Producer closed.")

if __name__ == "__main__":
    main()
