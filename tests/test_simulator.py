import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulator.fraud_injector import calculate_haversine_distance, FraudInjector
from simulator.profiles import generate_customers, generate_merchants
from simulator.transaction_generator import TransactionGenerator

class TestFraudSimulator(unittest.TestCase):
    def test_haversine_distance(self):
        # NY (40.7128, -74.0060) to LA (34.0522, -118.2437) ~ 3,930 km
        dist = calculate_haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        self.assertGreater(dist, 3900.0)
        self.assertLess(dist, 4000.0)

    def test_customer_profiles(self):
        customers = generate_customers(20)
        self.assertEqual(len(customers), 20)
        for c in customers:
            self.assertTrue(c.account_id.startswith("ACC-"))
            self.assertIsNotNone(c.home_location.city)
            self.assertGreater(c.typical_avg_amount, 0)

    def test_merchant_profiles(self):
        merchants = generate_merchants(10)
        self.assertEqual(len(merchants), 10)
        for m in merchants:
            self.assertTrue(m.merchant_id.startswith("MERCH-"))
            self.assertIn(m.category, ["Grocery", "Restaurants", "Retail", "Online Services", "Electronics", "Travel", "Luxury", "Gambling", "Crypto"])

    def test_transaction_generation(self):
        gen = TransactionGenerator(num_customers=30, num_merchants=10, fraud_rate=0.20)
        txs = list(gen.stream_transactions(count=50))
        self.assertEqual(len(txs), 50)
        
        fraud_count = sum(1 for tx in txs if tx.is_fraud == 1)
        self.assertGreater(fraud_count, 0)
        
        for tx in txs:
            self.assertTrue(tx.transaction_id.startswith("TXN-"))
            self.assertIn(tx.is_fraud, [0, 1])
            self.assertIsNotNone(tx.timestamp)
            self.assertGreaterEqual(tx.distance_from_home_km, 0.0)

if __name__ == "__main__":
    unittest.main()
