from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class Location:
    latitude: float
    longitude: float
    city: str
    country: str = "US"

    def to_dict(self):
        return asdict(self)

@dataclass
class CustomerProfile:
    account_id: str
    card_number: str
    first_name: str
    last_name: str
    home_location: Location
    typical_avg_amount: float
    typical_std_amount: float
    device_id: str
    ip_address: str

    def to_dict(self):
        d = asdict(self)
        d["home_location"] = self.home_location.to_dict()
        return d

@dataclass
class MerchantProfile:
    merchant_id: str
    merchant_name: str
    category: str
    risk_weight: float
    location: Location

    def to_dict(self):
        d = asdict(self)
        d["location"] = self.location.to_dict()
        return d

@dataclass
class Transaction:
    transaction_id: str
    account_id: str
    card_number: str
    timestamp: str
    amount: float
    merchant_id: str
    merchant_name: str
    category: str
    location: Location
    device_id: str
    ip_address: str
    distance_from_home_km: float = 0.0
    is_fraud: int = 0
    fraud_type: str = "NORMAL"
    fraud_score: Optional[float] = 0.0

    def model_dump(self):
        d = asdict(self)
        d["location"] = self.location.to_dict()
        return d

    def to_dict(self):
        return self.model_dump()
