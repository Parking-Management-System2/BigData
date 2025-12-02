import os
import time
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType, StructField
from pyspark.sql.functions import from_json, col, current_timestamp, udf
from src.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, DATABASE_URL, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from src.preprocessing import get_spark_session
from src.model import load_model, train_model
from src.config import MODEL_PATH, DATA_PATH

def run_consumer():
    print("Uruchamianie konsumenta Spark...", flush=True)
    spark = get_spark_session("TelcoChurnConsumer")

    # Sprawdzenie czy model istnieje, jeśli nie - wytrenowanie nowego
    if not os.path.exists(MODEL_PATH):
        print("Nie znaleziono modelu. Trenowanie nowego modelu...")
        if not os.path.exists(DATA_PATH):
             from src.data_loader import download_data
             download_data()
        train_model(DATA_PATH)
    else:
        # Sprawdź, czy macierz pomyłek istnieje, jeśli nie - wygeneruj ją
        from src.model import generate_confusion_matrix_from_existing_model
        confusion_matrix_path = os.path.join(os.path.dirname(MODEL_PATH), "confusion_matrix.json")
        if not os.path.exists(confusion_matrix_path):
            print("Model istnieje, ale macierz pomyłek nie. Próba wygenerowania...")
            if os.path.exists(DATA_PATH):
                generate_confusion_matrix_from_existing_model(DATA_PATH)
    
    model = load_model()
    print("Model załadowany.")
    print(f"Etapy modelu: {model.stages}")

    # Schemat
    schema = StructType([
        StructField("customerID", StringType()),
        StructField("tenure", IntegerType()),
        StructField("InternetService", StringType()),
        StructField("OnlineSecurity", StringType()),
        StructField("DeviceProtection", StringType()),
        StructField("TechSupport", StringType()),
        StructField("Contract", StringType()),
        StructField("PaymentMethod", StringType()),
        StructField("MonthlyCharges", DoubleType()),
        StructField("TotalCharges", DoubleType())
    ])

    # Czytanie ze strumienia
    kafka_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    parsed_stream = kafka_stream.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")
    
    # Predykcja
    prediction_stream = model.transform(parsed_stream)
    
    # Wyodrębnienie prawdopodobieństwa odejścia (Churn)
    # Kolumna 'probability' ze Spark ML jest wektorem.    
    get_prob_udf = udf(lambda v: float(v[1]), DoubleType())
    
    results = prediction_stream \
        .withColumn("churn_probability", get_prob_udf(col("probability"))) \
        .withColumn("timestamp", current_timestamp()) \
        .select("customerID", "prediction", "churn_probability", "timestamp")

    # Zapis paczki do PostgreSQL    
    def write_to_postgres(batch_df, _batch_id):
        batch_df.write \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}") \
            .option("dbtable", "churn_predictions") \
            .option("user", DB_USER) \
            .option("password", DB_PASSWORD) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
            
    print("Rozpoczynanie przetwarzania strumieniowego...")
    query = results.writeStream \
        .foreachBatch(write_to_postgres) \
        .start()
        
    query.awaitTermination()

if __name__ == "__main__":
    from src.config import KAFKA_INITIAL_WAIT_CONSUMER
    # Oczekiwanie na Kafkę i Bazę Danych
    time.sleep(KAFKA_INITIAL_WAIT_CONSUMER)
    run_consumer()
