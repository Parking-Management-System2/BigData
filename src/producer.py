import json
import time
import random
import os
from kafka import KafkaProducer
from src.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, DATA_PATH, KAFKA_INITIAL_WAIT_PRODUCER, PRODUCER_INTERVAL_MIN, PRODUCER_INTERVAL_MAX
from src.preprocessing import get_spark_session, load_and_clean_data

def create_producer():
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

def run_producer():
    # Oczekiwanie na gotowość Kafki
    time.sleep(KAFKA_INITIAL_WAIT_PRODUCER) 
    
    spark = get_spark_session("TelcoProducer")
    
    if not os.path.exists(DATA_PATH):
        print("Nie znaleziono danych, pobieranie...")
        from src.data_loader import download_data
        download_data()

    df = load_and_clean_data(spark, DATA_PATH)
    
    # Podział na zbiór treningowy i testowy
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)
    
    # Użycie zbioru testowego do strumieniowania (symulacja nowych danych)
    sample_data = test_data.collect()
    
    producer = create_producer()
    total_records = len(sample_data)
    current_index = 0
    
    print(f"Uruchamianie producenta. Całkowita liczba rekordów: {total_records}")
    
    while True: # Pętla nieskończona do ciągłego strumieniowania
        if current_index >= total_records:
            current_index = 0 # Restart
            
        batch_size = random.randint(50, 200)
        end_index = min(current_index + batch_size, total_records)
        batch = sample_data[current_index : end_index]
        
        for row in batch:
            data_dict = row.asDict()
            producer.send(KAFKA_TOPIC, value=data_dict)
            
        producer.flush()
        print(f"Wysłano paczkę {len(batch)} rekordów.")
        
        current_index = end_index
        time.sleep(random.uniform(PRODUCER_INTERVAL_MIN, PRODUCER_INTERVAL_MAX))

if __name__ == "__main__":
    run_producer()
