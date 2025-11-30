from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database import init_db, get_db
from backend.routers import analytics, predictions
import threading

app = FastAPI(title="Telco Churn API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Inicjalizacja bazy danych w osobnym wątku, aby uniknąć blokowania startu w przypadku powolnego działania bazy
    threading.Thread(target=init_db).start()


@app.get("/", tags=["Healthcheck"])
def health_check(db: Session = Depends(get_db)):
    try:
        # Sprawdzenie połączenia z bazą danych
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Database connection failed: {str(e)}"
        )


app.include_router(analytics.router)
app.include_router(predictions.router)
