from pydantic import BaseModel

class CustomerData(BaseModel):
    customerID: str
    tenure: int
    InternetService: str
    OnlineSecurity: str
    DeviceProtection: str
    TechSupport: str
    Contract: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float
