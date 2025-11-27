import os

# Konfiguracja Kafki
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "telco-churn")

# Konfiguracja Bazy Danych
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME = os.getenv("POSTGRES_DB", "churn_db")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Konfiguracja Sparka
SPARK_APP_NAME = "TelcoChurnProject"
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")

# Ścieżki
DATA_PATH = os.getenv("DATA_PATH", "/app/data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/rf_churn_model")

# Delays Configuration
KAFKA_INITIAL_WAIT_PRODUCER = int(os.getenv("KAFKA_INITIAL_WAIT_PRODUCER", "20"))
KAFKA_INITIAL_WAIT_CONSUMER = int(os.getenv("KAFKA_INITIAL_WAIT_CONSUMER", "20"))
PRODUCER_INTERVAL_MIN = float(os.getenv("PRODUCER_INTERVAL_MIN", "0.5"))
PRODUCER_INTERVAL_MAX = float(os.getenv("PRODUCER_INTERVAL_MAX", "1.0"))
DB_RETRY_DELAY = int(os.getenv("DB_RETRY_DELAY", "10"))
