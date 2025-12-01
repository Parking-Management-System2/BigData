export interface CustomerData {
    customerID: string;
    tenure: number;
    InternetService: string;
    OnlineSecurity: string;
    DeviceProtection: string;
    TechSupport: string;
    Contract: string;
    PaymentMethod: string;
    MonthlyCharges: number;
    TotalCharges: number;
}

export interface ChurnPrediction {
    id: number;
    customerID: string;
    prediction: number;
    churn_probability: number;
    timestamp: string;
}

export interface Stats {
    total_predictions: number;
    churn_count: number;
    no_churn_count: number;
    churn_rate: number;
}

export interface RiskDistribution {
    probabilities: number[];
}

export interface ChurnOverTimePoint {
    time: string;
    total: number;
    churn_count: number;
}

export interface CorrelationMatrix {
    matrix: Record<string, Record<string, number>>;
    features: string[];
    error?: string;
}

export interface ConfusionMatrix {
    matrix: number[][];
    labels: string[];
    metrics: {
        accuracy: number;
        precision: number;
        recall: number;
        f1_score: number;
        auc?: number;
    };
    error?: string;
}