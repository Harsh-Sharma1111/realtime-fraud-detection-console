import os

# Kafka Settings
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094,localhost:9092").split(",")
KAFKA_TOPIC_TRANSACTIONS = os.getenv("KAFKA_TOPIC_TRANSACTIONS", "banking-transactions")
KAFKA_TOPIC_FLAGGED = os.getenv("KAFKA_TOPIC_FLAGGED", "flagged-transactions")

# MongoDB Settings (Hot Storage)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "fraud_detection_db")
MONGO_COLL_TRANSACTIONS = "raw_transactions"
MONGO_COLL_ALERTS = "flagged_alerts"

# Spark Settings
SPARK_APP_NAME = "RealTimeFraudDetector"
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")

# Transaction Simulator Settings
SIMULATOR_NUM_CUSTOMERS = int(os.getenv("SIMULATOR_NUM_CUSTOMERS", "200"))
SIMULATOR_NUM_MERCHANTS = int(os.getenv("SIMULATOR_NUM_MERCHANTS", "50"))
SIMULATOR_DEFAULT_RATE = float(os.getenv("SIMULATOR_DEFAULT_RATE", "5.0"))  # transactions per second
FRAUD_INJECTION_RATE = float(os.getenv("FRAUD_INJECTION_RATE", "0.08"))     # 8% fraudulent transactions

# Merchant Categories & Risk Weights
MERCHANT_CATEGORIES = {
    "Grocery": 0.05,
    "Restaurants": 0.08,
    "Retail": 0.10,
    "Online Services": 0.15,
    "Electronics": 0.35,
    "Travel": 0.40,
    "Luxury": 0.65,
    "Gambling": 0.85,
    "Crypto": 0.90
}

HIGH_RISK_CATEGORIES = ["Gambling", "Crypto", "Luxury", "Electronics"]

# Rules Engine Thresholds
RULES_HIGH_AMOUNT_THRESHOLD = 2500.00
RULES_IMPOSSIBLE_TRAVEL_SPEED_KMH = 800.0  # Max realistic travel speed between consecutive txs
RULES_NIGHT_HOURS = (1, 4)                 # 1 AM to 4 AM
