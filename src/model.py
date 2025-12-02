import os
import json
from pyspark.ml.classification import RandomForestClassifier, RandomForestClassificationModel
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from src.config import MODEL_PATH
from src.preprocessing import get_spark_session, load_and_clean_data, build_pipeline
from pyspark.ml import Pipeline
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score


def train_model(data_path):
    spark = get_spark_session("TelcoChurnTraining")
    df = load_and_clean_data(spark, data_path)

    # Label indexing
    from pyspark.ml.feature import StringIndexer
    indexer = StringIndexer(inputCol="Churn", outputCol="label", handleInvalid="skip")
    df = indexer.fit(df).transform(df)

    train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

    pipeline = build_pipeline()

    # Random Forest
    rf = RandomForestClassifier(
        labelCol="label",
        featuresCol="features",
        seed=42
    )

    full_pipeline = Pipeline(stages=pipeline.getStages() + [rf])

    # Strojenie hiperparametrów
    param_grid = (
        ParamGridBuilder()
        .addGrid(rf.numTrees, [50, 100, 200])
        .addGrid(rf.maxDepth, [5, 10, 15])
        .addGrid(rf.maxBins, [32, 64])
        .build()
    )

    evaluator = BinaryClassificationEvaluator(labelCol="label")

    cv = CrossValidator(
        estimator=full_pipeline,
        estimatorParamMaps=param_grid,
        evaluator=evaluator,
        numFolds=5,  # 5-krotna walidacja krzyżowa
        parallelism=4 # Równoległe przetwarzanie
    )

    print("Trenowanie modelu z tuningiem hiperparametrów...")
    model = cv.fit(train_data)
    print("Model wytrenowany!")

    # Ewaluacja
    predictions = model.transform(test_data)
    auc = evaluator.evaluate(predictions)
    print(f"Test AUC: {auc}")

    # Obliczenie macierzy pomyłek
    print("Obliczanie macierzy pomyłek...")
    predictions_pd = predictions.select("label", "prediction").toPandas()
    y_true = predictions_pd["label"].values
    y_pred = predictions_pd["prediction"].values

    # Macierz pomyłek z sklearn
    cm = confusion_matrix(y_true, y_pred).tolist()

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    # Zapis macierzy pomyłek do pliku JSON
    confusion_matrix_data = {
        "matrix": cm,
        "labels": ["No Churn", "Churn"],
        "metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "auc": float(auc)
        }
    }
    
    confusion_matrix_path = os.path.join(os.path.dirname(MODEL_PATH), "confusion_matrix.json")
    os.makedirs(os.path.dirname(confusion_matrix_path), exist_ok=True)
    
    with open(confusion_matrix_path, 'w') as f:
        json.dump(confusion_matrix_data, f, indent=2)
    
    print(f"Macierz pomyłek zapisana do {confusion_matrix_path}")
    print(f"Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")

    # Zapis najlepszego modelu (PipelineModel)
    print(f"Zapisywanie modelu do {MODEL_PATH}...")
    model.bestModel.write().overwrite().save(MODEL_PATH)

    return model.bestModel


def generate_confusion_matrix_from_existing_model(data_path=None):
    """
    Generuje macierz pomyłek z istniejącego modelu, jeśli model istnieje, ale macierz nie.
    """
    if not os.path.exists(MODEL_PATH):
        print("Model nie istnieje. Nie można wygenerować macierzy pomyłek.")
        return False
    
    confusion_matrix_path = os.path.join(os.path.dirname(MODEL_PATH), "confusion_matrix.json")
    if os.path.exists(confusion_matrix_path):
        print("Macierz pomyłek już istnieje.")
        return True
    
    print("Model istnieje, ale macierz pomyłek nie. Generowanie macierzy...")
    
    if data_path is None:
        from src.config import DATA_PATH
        data_path = DATA_PATH
    
    if not os.path.exists(data_path):
        print(f"Plik danych nie istnieje: {data_path}")
        return False
    
    try:
        spark = get_spark_session("GenerateConfusionMatrix")
        df = load_and_clean_data(spark, data_path)
        
        # Label indexing
        from pyspark.ml.feature import StringIndexer
        indexer = StringIndexer(inputCol="Churn", outputCol="label", handleInvalid="skip")
        df = indexer.fit(df).transform(df)
        
        # Podział na train/test (używamy tego samego seeda co w train_model)
        train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)
        
        # Załadowanie modelu
        from pyspark.ml import PipelineModel
        model = PipelineModel.load(MODEL_PATH)
        
        # Predykcje
        predictions = model.transform(test_data)
        
        # Obliczenie macierzy pomyłek
        predictions_pd = predictions.select("label", "prediction").toPandas()
        y_true = predictions_pd["label"].values
        y_pred = predictions_pd["prediction"].values
        
        cm = confusion_matrix(y_true, y_pred).tolist()
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        
        # Obliczenie AUC
        evaluator = BinaryClassificationEvaluator(labelCol="label")
        auc = evaluator.evaluate(predictions)
        
        # Zapis
        confusion_matrix_data = {
            "matrix": cm,
            "labels": ["No Churn", "Churn"],
            "metrics": {
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1),
                "auc": float(auc)
            }
        }
        
        os.makedirs(os.path.dirname(confusion_matrix_path), exist_ok=True)
        with open(confusion_matrix_path, 'w') as f:
            json.dump(confusion_matrix_data, f, indent=2)
        
        print(f"Macierz pomyłek wygenerowana i zapisana do {confusion_matrix_path}")
        return True
    except Exception as e:
        print(f"Błąd podczas generowania macierzy pomyłek: {str(e)}")
        return False


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please train it first.")

    from pyspark.ml import PipelineModel
    return PipelineModel.load(MODEL_PATH)


if __name__ == "__main__":
    from src.config import DATA_PATH

    if not os.path.exists(DATA_PATH):
        from src.data_loader import download_data

        download_data()

    train_model(DATA_PATH)
