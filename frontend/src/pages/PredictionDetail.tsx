import { motion } from "framer-motion";
import {
    AlertCircle,
    AlertTriangle,
    ArrowLeft,
    Calendar,
    ChevronRight,
    Clock,
    Hash,
    Shield,
    TrendingUp,
    User,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
    Area,
    AreaChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { fetchCustomerHistory } from "../services/api";
import type { ChurnPrediction } from "../types";

const PredictionDetail: React.FC = () => {
    const { customerId, id } = useParams<{ customerId: string; id: string }>();
    const [prediction, setPrediction] = useState<ChurnPrediction | null>(null);
    const [customerHistory, setCustomerHistory] = useState<ChurnPrediction[]>(
        []
    );
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            if (!customerId || !id) return;

            try {
                setLoading(true);
                // Fetch all predictions for this customer
                const history = await fetchCustomerHistory(customerId);
                setCustomerHistory(history);

                // Find the specific prediction by ID
                const predictionData = history.find(
                    (p) => p.id === parseInt(id)
                );
                if (!predictionData) {
                    setError("Predykcja nie została znaleziona");
                    return;
                }
                setPrediction(predictionData);
            } catch (err) {
                setError("Nie udało się załadować danych predykcji");
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [customerId, id]);

    if (loading) {
        return (
            <div className="flex flex-col justify-center items-center h-[60vh] gap-4">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-primary/20 rounded-full" />
                    <div className="absolute top-0 left-0 w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                </div>
                <p className="text-text-secondary">Ładowanie danych...</p>
            </div>
        );
    }

    if (error || !prediction) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
                <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400">
                    <AlertTriangle className="w-12 h-12 mx-auto mb-2" />
                    <p className="text-center">
                        {error || "Predykcja nie została znaleziona"}
                    </p>
                </div>
                <Link
                    to="/"
                    className="flex items-center gap-2 text-primary hover:text-primary-light transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Powrót do panelu głównego
                </Link>
            </div>
        );
    }

    const probabilityPercent = (prediction.churn_probability * 100).toFixed(1);

    // Prepare history chart data (reverse to show oldest first)
    const historyChartData = [...customerHistory].reverse().map((p) => ({
        time: p.timestamp,
        probability: p.churn_probability,
        prediction: p.prediction,
    }));

    const getRiskLevel = (probability: number) => {
        if (probability >= 0.7)
            return {
                label: "Wysokie",
                color: "text-rose-400",
                bg: "bg-rose-500/10",
            };
        if (probability >= 0.4)
            return {
                label: "Średnie",
                color: "text-amber-400",
                bg: "bg-amber-500/10",
            };
        return {
            label: "Niskie",
            color: "text-emerald-400",
            bg: "bg-emerald-500/10",
        };
    };

    const riskLevel = getRiskLevel(prediction.churn_probability);

    return (
        <div className="space-y-8">
            {/* Breadcrumb */}
            <nav className="flex items-center gap-2 text-sm text-text-muted">
                <Link
                    to="/"
                    className="hover:text-text-primary transition-colors"
                >
                    Panel główny
                </Link>
                <ChevronRight className="w-4 h-4" />
                <span className="text-text-primary">Szczegóły predykcji</span>
            </nav>

            {/* Header */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
            >
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="h-8 w-1 bg-linear-to-b from-primary to-secondary rounded-full" />
                        <h1 className="text-4xl font-bold text-white">
                            Predykcja #{prediction.id}
                        </h1>
                    </div>
                    <p className="text-text-secondary ml-4 pl-3 border-l border-border">
                        Szczegółowa analiza ryzyka odpływu klienta
                    </p>
                </div>
                <Link
                    to="/"
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-surface border border-border text-text-secondary hover:text-text-primary hover:border-border-light transition-all"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Powrót
                </Link>
            </motion.header>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Prediction Result Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="card-glow lg:col-span-1"
                >
                    <h2 className="text-lg font-semibold text-white mb-6">
                        Wynik predykcji
                    </h2>

                    {/* Status Badge */}
                    <div className="flex justify-center mb-6">
                        <div
                            className={`inline-flex items-center gap-3 px-6 py-3 rounded-2xl text-lg font-semibold ${
                                prediction.churn_probability >= 0.7
                                    ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                    : prediction.churn_probability >= 0.4
                                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                    : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            }`}
                        >
                            {prediction.churn_probability >= 0.7 ? (
                                <>
                                    <AlertTriangle className="w-6 h-6" />
                                    Ryzyko odpływu
                                </>
                            ) : prediction.churn_probability >= 0.4 ? (
                                <>
                                    <AlertCircle className="w-6 h-6" />
                                    Możliwy odpływ
                                </>
                            ) : (
                                <>
                                    <Shield className="w-6 h-6" />
                                    Klient bezpieczny
                                </>
                            )}
                        </div>
                    </div>

                    {/* Probability Gauge */}
                    <div className="relative pt-4">
                        <div className="text-center mb-4">
                            <span className="text-5xl font-bold text-white">
                                {probabilityPercent}%
                            </span>
                            <p className="text-text-muted mt-1">
                                Prawdopodobieństwo odpływu
                            </p>
                        </div>

                        {/* Progress Bar */}
                        <div className="h-3 bg-surface rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{
                                    width: `${
                                        prediction.churn_probability * 100
                                    }%`,
                                }}
                                transition={{ duration: 1, ease: "easeOut" }}
                                className={`h-full rounded-full ${
                                    prediction.churn_probability >= 0.7
                                        ? "bg-linear-to-r from-rose-500 to-pink-500"
                                        : prediction.churn_probability >= 0.4
                                        ? "bg-linear-to-r from-amber-500 to-orange-500"
                                        : "bg-linear-to-r from-emerald-500 to-teal-500"
                                }`}
                            />
                        </div>

                        {/* Scale Labels */}
                        <div className="flex justify-between mt-2 text-xs text-text-muted">
                            <span>0%</span>
                            <span>50%</span>
                            <span>100%</span>
                        </div>
                    </div>

                    {/* Risk Level */}
                    <div className="mt-6 p-4 rounded-xl bg-surface/50 border border-border/50">
                        <div className="flex items-center justify-between">
                            <span className="text-text-muted">
                                Poziom ryzyka
                            </span>
                            <span
                                className={`px-3 py-1 rounded-lg text-sm font-medium ${riskLevel.bg} ${riskLevel.color}`}
                            >
                                {riskLevel.label}
                            </span>
                        </div>
                    </div>
                </motion.div>

                {/* Details Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="card-glow lg:col-span-2"
                >
                    <h2 className="text-lg font-semibold text-white mb-6">
                        Informacje szczegółowe
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Customer ID */}
                        <div className="p-4 rounded-xl bg-surface/50 border border-border/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-blue-500/10">
                                    <User className="w-5 h-5 text-blue-400" />
                                </div>
                                <div>
                                    <p className="text-xs text-text-muted uppercase tracking-wider">
                                        ID Klienta
                                    </p>
                                    <p className="text-lg font-semibold text-white">
                                        {prediction.customerID}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Prediction ID */}
                        <div className="p-4 rounded-xl bg-surface/50 border border-border/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-purple-500/10">
                                    <Hash className="w-5 h-5 text-purple-400" />
                                </div>
                                <div>
                                    <p className="text-xs text-text-muted uppercase tracking-wider">
                                        ID Predykcji
                                    </p>
                                    <p className="text-lg font-semibold text-white">
                                        #{prediction.id}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Timestamp */}
                        <div className="p-4 rounded-xl bg-surface/50 border border-border/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-cyan-500/10">
                                    <Calendar className="w-5 h-5 text-cyan-400" />
                                </div>
                                <div>
                                    <p className="text-xs text-text-muted uppercase tracking-wider">
                                        Data analizy
                                    </p>
                                    <p className="text-lg font-semibold text-white">
                                        {new Date(
                                            prediction.timestamp
                                        ).toLocaleDateString("pl-PL", {
                                            day: "numeric",
                                            month: "long",
                                            year: "numeric",
                                        })}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Time */}
                        <div className="p-4 rounded-xl bg-surface/50 border border-border/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-amber-500/10">
                                    <Clock className="w-5 h-5 text-amber-400" />
                                </div>
                                <div>
                                    <p className="text-xs text-text-muted uppercase tracking-wider">
                                        Godzina analizy
                                    </p>
                                    <p className="text-lg font-semibold text-white">
                                        {new Date(
                                            prediction.timestamp
                                        ).toLocaleTimeString("pl-PL", {
                                            hour: "2-digit",
                                            minute: "2-digit",
                                            second: "2-digit",
                                        })}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Recommendation */}
                    <div className="mt-6 p-4 rounded-xl border border-border/50 bg-surface/30">
                        <div className="flex items-start gap-3">
                            <div
                                className={`p-2 rounded-lg ${
                                    prediction.churn_probability >= 0.7
                                        ? "bg-rose-500/10"
                                        : prediction.churn_probability >= 0.4
                                        ? "bg-amber-500/10"
                                        : "bg-emerald-500/10"
                                }`}
                            >
                                <TrendingUp
                                    className={`w-5 h-5 ${
                                        prediction.churn_probability >= 0.7
                                            ? "text-rose-400"
                                            : prediction.churn_probability >=
                                              0.4
                                            ? "text-amber-400"
                                            : "text-emerald-400"
                                    }`}
                                />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-white mb-1">
                                    Rekomendacja
                                </p>
                                <p className="text-sm text-text-secondary">
                                    {prediction.churn_probability >= 0.7
                                        ? "Zalecamy natychmiastowy kontakt z klientem. Rozważ zaoferowanie specjalnej promocji lub rabatu, aby zatrzymać klienta. Przeanalizuj historię interakcji i zidentyfikuj potencjalne problemy."
                                        : prediction.churn_probability >= 0.4
                                        ? "Klient wymaga uwagi. Zalecamy proaktywny kontakt w celu zbadania satysfakcji. Rozważ personalizowane oferty lub ankietę satysfakcji, aby zapobiec potencjalnemu odpływowi."
                                        : "Klient wydaje się zadowolony z usług. Kontynuuj dotychczasową strategię obsługi. Rozważ programy lojalnościowe, aby wzmocnić relację."}
                                </p>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Customer History Chart */}
            {customerHistory.length > 1 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="card-glow"
                >
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-lg font-semibold text-white">
                                Historia predykcji klienta
                            </h2>
                            <p className="text-sm text-text-muted mt-1">
                                Trend prawdopodobieństwa odpływu w czasie
                            </p>
                        </div>
                        <span className="text-xs text-text-muted bg-surface px-3 py-1.5 rounded-lg border border-border">
                            {customerHistory.length} analiz
                        </span>
                    </div>

                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={historyChartData}>
                                <defs>
                                    <linearGradient
                                        id="colorHistory"
                                        x1="0"
                                        y1="0"
                                        x2="0"
                                        y2="1"
                                    >
                                        <stop
                                            offset="0%"
                                            stopColor="#6366f1"
                                            stopOpacity={0.4}
                                        />
                                        <stop
                                            offset="100%"
                                            stopColor="#6366f1"
                                            stopOpacity={0}
                                        />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke="#27272a"
                                    vertical={false}
                                />
                                <XAxis
                                    dataKey="time"
                                    stroke="#52525b"
                                    tickFormatter={(str) =>
                                        new Date(str).toLocaleDateString(
                                            "pl-PL",
                                            {
                                                day: "2-digit",
                                                month: "2-digit",
                                            }
                                        )
                                    }
                                    tick={{ fontSize: 12 }}
                                />
                                <YAxis
                                    stroke="#52525b"
                                    tick={{ fontSize: 12 }}
                                    domain={[0, 1]}
                                    tickFormatter={(value) =>
                                        `${(value * 100).toFixed(0)}%`
                                    }
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#1a1a24",
                                        borderColor: "#27272a",
                                        borderRadius: "12px",
                                    }}
                                    labelFormatter={(label) =>
                                        new Date(label).toLocaleString("pl-PL")
                                    }
                                    formatter={(value: number) => [
                                        `${(value * 100).toFixed(1)}%`,
                                        "Prawdopodobieństwo",
                                    ]}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="probability"
                                    stroke="#6366f1"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorHistory)"
                                    name="Prawdopodobieństwo"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>
            )}

            {/* Customer History Table */}
            {customerHistory.length > 1 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="card-glow overflow-hidden"
                >
                    <h2 className="text-lg font-semibold text-white mb-6">
                        Wszystkie analizy klienta
                    </h2>

                    <div className="overflow-x-auto -mx-6 px-6">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                                    <th className="pb-4 font-semibold">
                                        ID Predykcji
                                    </th>
                                    <th className="pb-4 font-semibold">Data</th>
                                    <th className="pb-4 font-semibold">
                                        Prawdopodobieństwo
                                    </th>
                                    <th className="pb-4 font-semibold">
                                        Status
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border/50">
                                {customerHistory.map((hist) => (
                                    <tr
                                        key={hist.id}
                                        className={`table-row ${
                                            hist.id === prediction.id
                                                ? "bg-primary/5"
                                                : ""
                                        }`}
                                    >
                                        <td className="py-4 text-white font-medium">
                                            #{hist.id}
                                            {hist.id === prediction.id && (
                                                <span className="ml-2 text-xs text-primary">
                                                    (aktualna)
                                                </span>
                                            )}
                                        </td>
                                        <td className="py-4 text-text-secondary text-sm">
                                            {new Date(
                                                hist.timestamp
                                            ).toLocaleString("pl-PL")}
                                        </td>
                                        <td className="py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-24 progress-bar">
                                                    <div
                                                        className={`progress-bar-fill ${
                                                            hist.churn_probability >=
                                                            0.7
                                                                ? "bg-linear-to-r from-rose-500 to-pink-500"
                                                                : hist.churn_probability >=
                                                                  0.4
                                                                ? "bg-linear-to-r from-amber-500 to-orange-500"
                                                                : "bg-linear-to-r from-emerald-500 to-teal-500"
                                                        }`}
                                                        style={{
                                                            width: `${
                                                                hist.churn_probability *
                                                                100
                                                            }%`,
                                                        }}
                                                    />
                                                </div>
                                                <span className="text-sm text-text-secondary font-medium">
                                                    {(
                                                        hist.churn_probability *
                                                        100
                                                    ).toFixed(1)}
                                                    %
                                                </span>
                                            </div>
                                        </td>
                                        <td className="py-4">
                                            <span
                                                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
                                                    hist.churn_probability >=
                                                    0.7
                                                        ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                                        : hist.churn_probability >=
                                                          0.4
                                                        ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                                        : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                                }`}
                                            >
                                                {hist.churn_probability >=
                                                0.7 ? (
                                                    <>
                                                        <AlertTriangle className="w-3 h-3" />
                                                        Ryzyko
                                                    </>
                                                ) : hist.churn_probability >=
                                                  0.4 ? (
                                                    <>
                                                        <AlertCircle className="w-3 h-3" />
                                                        Możliwy
                                                    </>
                                                ) : (
                                                    <>
                                                        <Shield className="w-3 h-3" />
                                                        Bezpieczny
                                                    </>
                                                )}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </motion.div>
            )}
        </div>
    );
};

export default PredictionDetail;
