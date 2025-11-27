from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db, ChurnPrediction
import pandas as pd

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
