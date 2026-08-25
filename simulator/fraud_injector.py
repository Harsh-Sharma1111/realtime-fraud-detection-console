import math
import random

from typing import Tuple, Dict, Any
from simulator.schema import CustomerProfile, MerchantProfile, Location
from config.settings import RULES_HIGH_AMOUNT_THRESHOLD, HIGH_RISK_CATEGORIES
from simulator.profiles import US_CITIES

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great-circle distance between two points on the Earth in kilometers."""
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class FraudInjector:
    def __init__(self, fraud_rate: float = 0.08):
        self.fraud_rate = fraud_rate
        self.fraud_patterns = [
            "HIGH_AMOUNT",
            "IMPOSSIBLE_VELOCITY",
            "ODD_HOURS",
            "HIGH_RISK_MERCHANT"
        ]

    def inject_fraud_if_selected(
        self,
        customer: CustomerProfile,
        merchant: MerchantProfile,
        base_amount: float,
        timestamp_str: str,
        last_tx_location: Location = None
    ) -> Tuple[int, str, float, Location, MerchantProfile, str]:
        """
        Determines whether to inject fraud.
        Returns: (is_fraud, fraud_type, adjusted_amount, transaction_location, merchant, timestamp_str)
        """
        if random.random() > self.fraud_rate:
            # Normal Transaction
            # Location is close to merchant or home
            tx_loc = Location(
                latitude=round(merchant.location.latitude + random.uniform(-0.02, 0.02), 6),
                longitude=round(merchant.location.longitude + random.uniform(-0.02, 0.02), 6),
                city=merchant.location.city,
                country="US"
            )
            return 0, "NORMAL", base_amount, tx_loc, merchant, timestamp_str

        # Fraudulent Transaction Selected
        fraud_type = random.choice(self.fraud_patterns)

        if fraud_type == "HIGH_AMOUNT":
            # 1. Sudden High Amount Spike ($2,500 - $9,500)
            adjusted_amount = round(random.uniform(RULES_HIGH_AMOUNT_THRESHOLD, 9500.0), 2)
            tx_loc = merchant.location
            return 1, fraud_type, adjusted_amount, tx_loc, merchant, timestamp_str

        elif fraud_type == "IMPOSSIBLE_VELOCITY":
            # 2. Impossible Travel (Pick distant city > 1,500 km away)
            distant_cities = [c for c in US_CITIES if c["city"] != customer.home_location.city]
            chosen_city = random.choice(distant_cities)
            tx_loc = Location(
                latitude=round(chosen_city["lat"] + random.uniform(-0.01, 0.01), 6),
                longitude=round(chosen_city["lon"] + random.uniform(-0.01, 0.01), 6),
                city=chosen_city["city"],
                country="US"
            )
            adjusted_amount = round(base_amount * random.uniform(2.5, 6.0), 2)
            return 1, fraud_type, adjusted_amount, tx_loc, merchant, timestamp_str

        elif fraud_type == "ODD_HOURS":
            # 3. Nighttime Burst (Forces 01:30 AM to 03:50 AM)
            dt_parts = timestamp_str.split("T")
            odd_hour = random.randint(1, 3)
            odd_minute = random.randint(10, 50)
            time_part = f"{odd_hour:02d}:{odd_minute:02d}:{random.randint(10,59):02d}Z"
            odd_timestamp = f"{dt_parts[0]}T{time_part}"
            
            adjusted_amount = round(random.uniform(800.0, 3200.0), 2)
            tx_loc = merchant.location
            return 1, fraud_type, adjusted_amount, tx_loc, merchant, odd_timestamp

        elif fraud_type == "HIGH_RISK_MERCHANT":
            # 4. Merchant Risk Category Mismatch (Crypto/Gambling/Luxury)
            risk_cat = random.choice(HIGH_RISK_CATEGORIES)
            adjusted_merchant = MerchantProfile(
                merchant_id=f"RISK-{random.randint(9000, 9999)}",
                merchant_name=f"HighRisk-{risk_cat}-Gateway",
                category=risk_cat,
                risk_weight=0.90,
                location=merchant.location
            )
            adjusted_amount = round(random.uniform(1200.0, 4800.0), 2)
            return 1, fraud_type, adjusted_amount, merchant.location, adjusted_merchant, timestamp_str

        return 0, "NORMAL", base_amount, merchant.location, merchant, timestamp_str
