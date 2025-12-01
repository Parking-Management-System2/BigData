from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db, ChurnPrediction
import pandas as pd
import os
import numpy as np
from typing import Dict, List

router = APIRouter(tags=["analytics"])

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    # Pobranie danych do DataFrame
    query = db.query(ChurnPrediction).statement
    df = pd.read_sql(query, db.bind)
    
    if df.empty:
        return {
            "total_predictions": 0,
            "churn_count": 0,
            "no_churn_count": 0,
            "churn_rate": 0
        }

    total = len(df)
    churn_count = int(df[df['prediction'] == 1.0].shape[0])
    no_churn_count = total - churn_count
    
    return {
        "total_predictions": total,
        "churn_count": churn_count,
        "no_churn_count": no_churn_count,
        "churn_rate": churn_count / total if total > 0 else 0
    }

@router.get("/risk-distribution")
def get_risk_distribution(limit: int = 1000, db: Session = Depends(get_db)):
    # Pobranie ostatnich 'limit' rekordów do DataFrame
    query = db.query(ChurnPrediction.churn_probability).order_by(ChurnPrediction.timestamp.desc()).limit(limit).statement
    df = pd.read_sql(query, db.bind)
    
    if df.empty:
        return {"probabilities": []}
        
    probs = df['churn_probability'].tolist()
    return {"probabilities": probs}

@router.get("/churn-over-time")
def get_churn_over_time(limit: int = 10000, window: int = 60, db: Session = Depends(get_db)):
    # Pobranie danych do DataFrame
    query = db.query(ChurnPrediction.timestamp, ChurnPrediction.prediction).order_by(ChurnPrediction.timestamp.desc()).limit(limit).statement
    df = pd.read_sql(query, db.bind)
    
    if df.empty:
        return []

    # Konwersja na datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Zaokrąglenie do minuty (floor)
    df['bucket'] = df['timestamp'].dt.floor('min')
    
    # Grupowanie
    grouped = df.groupby('bucket').agg(
        total=('prediction', 'count'),
        churn_count=('prediction', 'sum')
    ).reset_index().sort_values('bucket')
    
    # Ograniczenie do ostatnich 'window' minut (rekordów)
    grouped = grouped.tail(window)
    
    data = []
    for _, row in grouped.iterrows():
        data.append({
            "time": row['bucket'],
            "total": int(row['total']),
            "churn_count": int(row['churn_count'])
        })
        
    return data

@router.get("/correlation-matrix")
def get_correlation_matrix():
    """
    Oblicza macierz korelacji dla numerycznych cech z danych treningowych.
    """
    # Ścieżka do danych
    data_path = os.getenv("DATA_PATH", "/app/data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
    
    # Jeśli nie ma w zmiennej środowiskowej, spróbuj lokalnej ścieżki
    if not os.path.exists(data_path):
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 "data", "WA_Fn-UseC_-Telco-Customer-Churn.csv")
    
    if not os.path.exists(data_path):
        return {
            "error": "Plik danych nie został znaleziony",
            "matrix": {},
            "features": []
        }
    
    try:
        # Wczytanie danych
        df = pd.read_csv(data_path)
        
        # Wybór tylko numerycznych kolumn
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Usunięcie kolumny customerID jeśli istnieje (nie jest numeryczna w sensie korelacji)
        # oraz innych kolumn, które nie powinny być w macierzy korelacji
        cols_to_remove = ['customerID']
        for col in cols_to_remove:
            if col in numeric_cols:
                numeric_cols.remove(col)
        
        # Obliczenie macierzy korelacji
        corr_matrix = df[numeric_cols].corr()
        
        # Konwersja do formatu JSON (słownik słowników)
        matrix_dict = {}
        for i, col1 in enumerate(numeric_cols):
            matrix_dict[col1] = {}
            for j, col2 in enumerate(numeric_cols):
                matrix_dict[col1][col2] = float(corr_matrix.loc[col1, col2])
        
        return {
            "matrix": matrix_dict,
            "features": numeric_cols
        }
    except Exception as e:
        return {
            "error": str(e),
            "matrix": {},
            "features": []
        }

@router.get("/confusion-matrix")
def get_confusion_matrix():
    """
    Zwraca macierz pomyłek z ostatniego treningu modelu.
    Macierz jest zapisywana podczas treningu w pliku JSON.
    """
    import json
    
    # Ścieżka do zapisanego pliku z macierzą pomyłek
    confusion_matrix_path = os.getenv("CONFUSION_MATRIX_PATH", "/app/models/confusion_matrix.json")
    
    # Lista ścieżek do sprawdzenia
    paths_to_check = [confusion_matrix_path]
    
    # Jeśli nie ma w zmiennej środowiskowej, spróbuj lokalnej ścieżki
    if not os.path.exists(confusion_matrix_path):
        # Spróbuj w katalogu models (gdzie model.py zapisuje)
        fallback_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "models", "confusion_matrix.json"
        )
        paths_to_check.append(fallback_path)
        if os.path.exists(fallback_path):
            confusion_matrix_path = fallback_path
        else:
            # Spróbuj w podkatalogu rf_churn_model
            alternative_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "models", "rf_churn_model", "confusion_matrix.json"
            )
            paths_to_check.append(alternative_path)
            if os.path.exists(alternative_path):
                confusion_matrix_path = alternative_path
    
    if not os.path.exists(confusion_matrix_path):
        # Sprawdź, czy katalog models istnieje
        models_dir = "/app/models"
        models_dir_exists = os.path.exists(models_dir)
        models_dir_contents = []
        if models_dir_exists:
            try:
                models_dir_contents = os.listdir(models_dir)
            except:
                pass
        
        error_msg = f"Macierz pomyłek nie została jeszcze wygenerowana. Model musi być najpierw wytrenowany."
        error_msg += f" Sprawdzane ścieżki: {', '.join(paths_to_check)}"
        if models_dir_exists:
            error_msg += f" Katalog /app/models istnieje. Zawartość: {', '.join(models_dir_contents[:10])}"
        
        return {
            "error": error_msg,
            "matrix": [[0, 0], [0, 0]],
            "labels": ["No Churn", "Churn"],
            "metrics": {}
        }
    
    try:
        with open(confusion_matrix_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {
            "error": f"Błąd podczas wczytywania macierzy pomyłek: {str(e)}",
            "matrix": [[0, 0], [0, 0]],
            "labels": ["No Churn", "Churn"],
            "metrics": {}
        }
