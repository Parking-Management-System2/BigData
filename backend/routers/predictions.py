from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, ChurnPrediction
from backend.schemas import CustomerData
from backend.kafka_client import get_producer
from src.config import KAFKA_TOPIC

router = APIRouter(tags=["predictions"])

@router.get("/recent")
def get_recent(limit: int = 10, db: Session = Depends(get_db)):
    results = db.query(ChurnPrediction).order_by(ChurnPrediction.timestamp.desc()).limit(limit).all()
    return results

@router.post("/submit")
def submit_customer(data: CustomerData):
    prod = get_producer()
    if prod:
        prod.send(KAFKA_TOPIC, value=data.dict())
        prod.flush()
        return {"message": "Dane przesłane pomyślnie", "customerID": data.customerID}
    else:
        return {"error": "Producent Kafka niedostępny"}

@router.get("/predictions/{customer_id}")
def get_customer_predictions(customer_id: str, db: Session = Depends(get_db)):
    predictions = db.query(ChurnPrediction).filter(ChurnPrediction.customerID == customer_id).order_by(ChurnPrediction.timestamp.desc()).all()
    
    if not predictions:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    return predictions
