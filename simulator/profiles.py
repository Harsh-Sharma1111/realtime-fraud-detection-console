import random
import uuid
from faker import Faker
from typing import List
from simulator.schema import CustomerProfile, MerchantProfile, Location
from config.settings import MERCHANT_CATEGORIES, SIMULATOR_NUM_CUSTOMERS, SIMULATOR_NUM_MERCHANTS

fake = Faker()
Faker.seed(42)
random.seed(42)

# Major US City Coordinates for realistic travel/distance calculations
US_CITIES = [
    {"city": "New York", "lat": 40.7128, "lon": -74.0060},
    {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
    {"city": "Chicago", "lat": 41.8781, "lon": -87.6298},
    {"city": "Houston", "lat": 29.7604, "lon": -95.3698},
    {"city": "Phoenix", "lat": 33.4484, "lon": -112.0740},
    {"city": "Philadelphia", "lat": 39.9526, "lon": -75.1652},
    {"city": "San Antonio", "lat": 29.4241, "lon": -98.4936},
    {"city": "San Diego", "lat": 32.7157, "lon": -117.1611},
    {"city": "Dallas", "lat": 32.7767, "lon": -96.7970},
    {"city": "San Jose", "lat": 37.3382, "lon": -121.8863},
    {"city": "Austin", "lat": 30.2672, "lon": -97.7431},
    {"city": "Miami", "lat": 25.7617, "lon": -80.1918},
    {"city": "Seattle", "lat": 47.6062, "lon": -122.3321},
    {"city": "Boston", "lat": 42.3601, "lon": -71.0589},
    {"city": "Denver", "lat": 39.7392, "lon": -104.9903}
]

def generate_customers(n: int = SIMULATOR_NUM_CUSTOMERS) -> List[CustomerProfile]:
    customers = []
    for i in range(n):
        city_info = random.choice(US_CITIES)
        # Add slight jitter to lat/lon for neighbourhood variability
        lat = city_info["lat"] + random.uniform(-0.05, 0.05)
        lon = city_info["lon"] + random.uniform(-0.05, 0.05)
        
        home_loc = Location(
            latitude=round(lat, 6),
            longitude=round(lon, 6),
            city=city_info["city"],
            country="US"
        )
        
        avg_amt = round(random.uniform(20.0, 150.0), 2)
        std_amt = round(avg_amt * random.uniform(0.15, 0.40), 2)
        
        c = CustomerProfile(
            account_id=f"ACC-{100000 + i}",
            card_number=fake.credit_card_number(card_type=None),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            home_location=home_loc,
            typical_avg_amount=avg_amt,
            typical_std_amount=std_amt,
            device_id=f"DEV-{uuid.uuid4().hex[:8].upper()}",
            ip_address=fake.ipv4()
        )
        customers.append(c)
    return customers

def generate_merchants(n: int = SIMULATOR_NUM_MERCHANTS) -> List[MerchantProfile]:
    merchants = []
    categories = list(MERCHANT_CATEGORIES.keys())
    for i in range(n):
        city_info = random.choice(US_CITIES)
        cat = random.choice(categories)
        risk_w = MERCHANT_CATEGORIES[cat]
        
        loc = Location(
            latitude=round(city_info["lat"] + random.uniform(-0.08, 0.08), 6),
            longitude=round(city_info["lon"] + random.uniform(-0.08, 0.08), 6),
            city=city_info["city"],
            country="US"
        )
        
        m = MerchantProfile(
            merchant_id=f"MERCH-{50000 + i}",
            merchant_name=f"{fake.company()} ({cat})",
            category=cat,
            risk_weight=risk_w,
            location=loc
        )
        merchants.append(m)
    return merchants
