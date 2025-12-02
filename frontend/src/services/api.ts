import axios from "axios";
import type {
    ChurnOverTimePoint,
    ChurnPrediction,
    CorrelationMatrix,
    ConfusionMatrix,
    CustomerData,
    RiskDistribution,
    Stats,
} from "../types";

// Use /api proxy in production (Docker), direct URL in development
const API_URL = import.meta.env.PROD ? "/api" : "http://localhost:8000";

const api = axios.create({
    baseURL: API_URL,
});

export const fetchStats = async (): Promise<Stats> => {
    const response = await api.get("/stats");
    return response.data;
};

export const fetchRiskDistribution = async (
    limit: number = 1000
): Promise<RiskDistribution> => {
    const response = await api.get("/risk-distribution", { params: { limit } });
    return response.data;
};

export const fetchChurnOverTime = async (
    limit: number = 10000,
    window: number = 60
): Promise<ChurnOverTimePoint[]> => {
    const response = await api.get("/churn-over-time", {
        params: { limit, window },
    });
    return response.data;
};

export const fetchRecentPredictions = async (
    limit: number = 10
): Promise<ChurnPrediction[]> => {
    const response = await api.get("/recent", { params: { limit } });
    return response.data;
};

export const submitPrediction = async (data: CustomerData) => {
    const response = await api.post("/submit", data);
    return response.data;
};

export const fetchCustomerHistory = async (
    customerId: string
): Promise<ChurnPrediction[]> => {
    const response = await api.get(`/predictions/${customerId}`);
    return response.data;
};

export const fetchCorrelationMatrix = async (): Promise<CorrelationMatrix> => {
    const response = await api.get("/correlation-matrix");
    return response.data;
};

export const fetchConfusionMatrix = async (): Promise<ConfusionMatrix> => {
    const response = await api.get("/confusion-matrix");
    return response.data;
};
