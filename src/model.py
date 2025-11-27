import os
from pyspark.ml.classification import RandomForestClassifier, RandomForestClassificationModel
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from src.config import MODEL_PATH
from src.preprocessing import get_spark_session, load_and_clean_data, build_pipeline

def train_model(data_path):
    spark = get_spark_session("TelcoChurnTraining")
    df = load_and_clean_data(spark, data_path)
    
    # Indeksowanie etykiet (Label Indexing) - tylko dla treningu
    from pyspark.ml.feature import StringIndexer
    indexer = StringIndexer(inputCol="Churn", outputCol="label", handleInvalid="skip")
    df = indexer.fit(df).transform(df)
    
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)
    
    pipeline = build_pipeline()
    
    # Dodanie modelu do potoku (Pipeline)
    rf = RandomForestClassifier(labelCol="label", featuresCol="features", seed=42)
    from pyspark.ml import Pipeline
    full_pipeline = Pipeline(stages=pipeline.getStages() + [rf])
    
    # Dopasowanie potoku bezpośrednio
    print("Trenowanie modelu...")
    model = full_pipeline.fit(train_data)
    print("Model wytrenowany!")
    
    # Ewaluacja
    predictions = model.transform(test_data)
    evaluator = BinaryClassificationEvaluator(labelCol="label")
    auc = evaluator.evaluate(predictions)
    print(f"Test AUC: {auc}")
    
    # Zapis modelu
    print(f"Zapisywanie modelu do {MODEL_PATH}...")
    model.write().overwrite().save(MODEL_PATH)
    
    return model

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please train it first.")
    
    # Ładowanie PipelineModel
    from pyspark.ml import PipelineModel
    return PipelineModel.load(MODEL_PATH)

if __name__ == "__main__":
    from src.config import DATA_PATH
    # Weryfikacja istnienia danych
    if not os.path.exists(DATA_PATH):
        from src.data_loader import download_data
        download_data()
        
    train_model(DATA_PATH)
