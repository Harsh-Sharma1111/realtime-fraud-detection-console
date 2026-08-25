import random
import uuid

from datetime import datetime, timezone
from typing import Generator, Dict, List
from simulator.schema import Transaction, Location
from simulator.profiles import generate_customers, generate_merchants
from simulator.fraud_injector import FraudInjector, calculate_haversine_distance
from config.settings import FRAUD_INJECTION_RATE, SIMULATOR_NUM_CUSTOMERS, SIMULATOR_NUM_MERCHANTS

class TransactionGenerator:
    def __init__(
        self,
        num_customers: int = SIMULATOR_NUM_CUSTOMERS,
        num_merchants: int = SIMULATOR_NUM_MERCHANTS,
        fraud_rate: float = FRAUD_INJECTION_RATE
    ):
        self.customers = generate_customers(num_customers)
        self.merchants = generate_merchants(num_merchants)
        self.fraud_injector = FraudInjector(fraud_rate=fraud_rate)
        self.customer_last_location: Dict[str, Location] = {}

    def generate_single_transaction(self) -> Transaction:
        customer = random.choice(self.customers)
        merchant = random.choice(self.merchants)
        
        # Calculate normal amount based on customer profile
        base_amount = max(
            5.0,
            round(random.gauss(customer.typical_avg_amount, customer.typical_std_amount), 2)
        )
        
        timestamp_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        last_loc = self.customer_last_location.get(customer.account_id, customer.home_location)
        
        (
            is_fraud,
            fraud_type,
            final_amount,
            tx_location,
            final_merchant,
            final_timestamp
        ) = self.fraud_injector.inject_fraud_if_selected(
            customer=customer,
            merchant=merchant,
            base_amount=base_amount,
            timestamp_str=timestamp_now,
            last_tx_location=last_loc
        )
        
        dist_km = calculate_haversine_distance(
            customer.home_location.latitude,
            customer.home_location.longitude,
            tx_location.latitude,
            tx_location.longitude
        )
        
        # Update last location for velocity tracking
        self.customer_last_location[customer.account_id] = tx_location
        
        tx = Transaction(
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            account_id=customer.account_id,
            card_number=customer.card_number,
            timestamp=final_timestamp,
            amount=final_amount,
            merchant_id=final_merchant.merchant_id,
            merchant_name=final_merchant.merchant_name,
            category=final_merchant.category,
            location=tx_location,
            device_id=customer.device_id,
            ip_address=customer.ip_address,
            distance_from_home_km=dist_km,
            is_fraud=is_fraud,
            fraud_type=fraud_type
        )
        return tx

    def stream_transactions(self, count: int = None) -> Generator[Transaction, None, None]:
        produced = 0
        while True:
            if count is not None and produced >= count:
                break
            yield self.generate_single_transaction()
            produced += 1
