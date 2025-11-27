from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL, DB_RETRY_DELAY
import time

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    id = Column(Integer, primary_key=True, index=True)
    customerID = Column(String, index=True)
    prediction = Column(Float)
    churn_probability = Column(Float)
    timestamp = Column(DateTime)

def init_db():
    # Logika ponawiania prób
    for i in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            print("Baza danych zainicjalizowana.")
            break
        except Exception as e:
            print(f"Baza danych niegotowa, ponawianie... ({e})")
            time.sleep(DB_RETRY_DELAY)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
