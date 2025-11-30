import { motion } from "framer-motion";
import {
    AlertTriangle,
    ChevronRight,
    Clock,
    Shield,
    TrendingUp,
    UserCheck,
    UserMinus,
    Users,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Area,
    AreaChart,
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import {
    fetchChurnOverTime,
    fetchRecentPredictions,
    fetchRiskDistribution,
    fetchStats,
} from "../services/api";
import type {
    ChurnOverTimePoint,
    ChurnPrediction,
    RiskDistribution,
    Stats,
} from "../types";

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState<Stats | null>(null);
    const [churnData, setChurnData] = useState<ChurnOverTimePoint[]>([]);
    const [riskData, setRiskData] = useState<RiskDistribution | null>(null);
    const [recentPredictions, setRecentPredictions] = useState<
        ChurnPrediction[]
    >([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [statsRes, churnRes, riskRes, recentRes] =
                    await Promise.all([
                        fetchStats(),
                        fetchChurnOverTime(),
                        fetchRiskDistribution(),
                        fetchRecentPredictions(),
                    ]);
                setStats(statsRes);
                setChurnData(churnRes);
                setRiskData(riskRes);
                setRecentPredictions(recentRes);
            } catch (error) {
                console.error("Failed to load dashboard data", error);
            } finally {
                setLoading(false);
            }
        };
        loadData();
        const interval = setInterval(loadData, 5000);
        return () => clearInterval(interval);
    }, []);

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

    const statCards = [
        {
            label: "Wszystkie predykcje",
            value: stats?.total_predictions || 0,
            icon: Users,
            gradient: "from-blue-500 to-cyan-500",
            bgGlow: "bg-blue-500/10",
        },
        {
            label: "Wykryty odpływ",
            value: stats?.churn_count || 0,
            icon: UserMinus,
            gradient: "from-rose-500 to-pink-500",
            bgGlow: "bg-rose-500/10",
        },
        {
            label: "Bezpieczni klienci",
            value: stats?.no_churn_count || 0,
            icon: UserCheck,
            gradient: "from-emerald-500 to-teal-500",
            bgGlow: "bg-emerald-500/10",
        },
        {
            label: "Wskaźnik odpływu",
            value: `${((stats?.churn_rate || 0) * 100).toFixed(1)}%`,
            icon: TrendingUp,
            gradient: "from-amber-500 to-orange-500",
            bgGlow: "bg-amber-500/10",
        },
    ];

    const riskChartData =
        riskData?.probabilities.map((prob, index) => ({
            index,
            probability: prob,
        })) || [];

    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative"
            >
                <div className="flex items-center gap-3 mb-2">
                    <div className="h-8 w-1 bg-linear-to-b from-primary to-secondary rounded-full" />
                    <h1 className="text-4xl font-bold text-white">
                        Panel główny
                    </h1>
                </div>
                <p className="text-text-secondary ml-4 pl-3 border-l border-border">
                    Przegląd predykcji odpływu klientów w czasie rzeczywistym
                </p>
            </motion.header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                {statCards.map((stat, index) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1, duration: 0.5 }}
                        className="stat-card"
                    >
                        <div
                            className={`relative p-3 rounded-xl ${stat.bgGlow}`}
                        >
                            <div
                                className={`absolute inset-0 bg-linear-to-br ${stat.gradient} opacity-20 rounded-xl blur-sm`}
                            />
                            <stat.icon
                                className={`relative w-6 h-6 bg-linear-to-br ${stat.gradient} bg-clip-text`}
                                style={{
                                    color: "transparent",
                                    background: `linear-gradient(135deg, var(--tw-gradient-from), var(--tw-gradient-to))`,
                                    WebkitBackgroundClip: "text",
                                }}
                            />
                            <stat.icon
                                className={`absolute inset-0 m-3 w-6 h-6 text-white opacity-80`}
                            />
                        </div>
                        <div className="flex-1">
                            <p className="text-sm text-text-muted font-medium">
                                {stat.label}
                            </p>
                            <p className="text-2xl font-bold text-white mt-0.5">
                                {stat.value}
                            </p>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Chart */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4 }}
                    className="card-glow lg:col-span-2"
                >
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-xl font-semibold text-white">
                                Trend odpływu
                            </h2>
                            <p className="text-sm text-text-muted flex items-center gap-1 mt-1">
                                <Clock className="w-3 h-3" /> Ostatnia godzina
                            </p>
                        </div>
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/20">
                            <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                            <span className="text-xs text-rose-400 font-medium">
                                Na żywo
                            </span>
                        </div>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={churnData}>
                                <defs>
                                    <linearGradient
                                        id="colorChurn"
                                        x1="0"
                                        y1="0"
                                        x2="0"
                                        y2="1"
                                    >
                                        <stop
                                            offset="0%"
                                            stopColor="#f43f5e"
                                            stopOpacity={0.4}
                                        />
                                        <stop
                                            offset="100%"
                                            stopColor="#f43f5e"
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
                                        new Date(str).toLocaleTimeString(
                                            "pl-PL",
                                            {
                                                hour: "2-digit",
                                                minute: "2-digit",
                                            }
                                        )
                                    }
                                    tick={{ fontSize: 12 }}
                                />
                                <YAxis
                                    stroke="#52525b"
                                    tick={{ fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: "#1a1a24",
                                        borderColor: "#27272a",
                                        borderRadius: "12px",
                                        boxShadow:
                                            "0 10px 40px rgba(0,0,0,0.4)",
                                    }}
                                    itemStyle={{ color: "#fafafa" }}
                                    labelFormatter={(label) =>
                                        new Date(label).toLocaleString("pl-PL")
                                    }
                                    labelStyle={{
                                        color: "#a1a1aa",
                                        marginBottom: "4px",
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="churn_count"
                                    stroke="#f43f5e"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorChurn)"
                                    name="Odpływy"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                {/* Risk Distribution */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                    className="card-glow"
                >
                    <div className="mb-6">
                        <h2 className="text-xl font-semibold text-white">
                            Rozkład ryzyka
                        </h2>
                        <p className="text-sm text-text-muted mt-1">
                            Prawdopodobieństwa odpływu
                        </p>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={riskChartData.slice(0, 50)}>
                                <defs>
                                    <linearGradient
                                        id="colorRisk"
                                        x1="0"
                                        y1="0"
                                        x2="0"
                                        y2="1"
                                    >
                                        <stop
                                            offset="0%"
                                            stopColor="#a855f7"
                                            stopOpacity={0.4}
                                        />
                                        <stop
                                            offset="100%"
                                            stopColor="#a855f7"
                                            stopOpacity={0}
                                        />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke="#27272a"
                                    vertical={false}
                                />
                                <XAxis hide />
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
                                    labelStyle={{ display: "none" }}
                                    formatter={(value: number) => [
                                        `${(value * 100).toFixed(1)}%`,
                                        "Prawdopodobieństwo",
                                    ]}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="probability"
                                    stroke="#a855f7"
                                    strokeWidth={2}
                                    dot={{
                                        fill: "#a855f7",
                                        strokeWidth: 0,
                                        r: 3,
                                    }}
                                    activeDot={{
                                        fill: "#c084fc",
                                        strokeWidth: 0,
                                        r: 5,
                                    }}
                                    name="Prawdopodobieństwo"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>
            </div>

            {/* Recent Predictions Table */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="card-glow overflow-hidden"
            >
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-xl font-semibold text-white">
                            Ostatnie predykcje
                        </h2>
                        <p className="text-sm text-text-muted mt-1">
                            Najnowsze analizy klientów
                        </p>
                    </div>
                    <span className="text-xs text-text-muted bg-surface px-3 py-1.5 rounded-lg border border-border">
                        {recentPredictions.length} wyników
                    </span>
                </div>
                <div className="overflow-x-auto -mx-6 px-6">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                                <th className="pb-4 font-semibold">
                                    ID Klienta
                                </th>
                                <th className="pb-4 font-semibold">Czas</th>
                                <th className="pb-4 font-semibold">
                                    Prawdopodobieństwo
                                </th>
                                <th className="pb-4 font-semibold">Status</th>
                                <th className="pb-4 font-semibold sr-only">
                                    Akcja
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border/50">
                            {recentPredictions.map((pred, idx) => (
                                <motion.tr
                                    key={pred.id}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.7 + idx * 0.05 }}
                                    className="table-row cursor-pointer group"
                                    onClick={() =>
                                        navigate(
                                            `/prediction/${pred.customerID}/${pred.id}`
                                        )
                                    }
                                >
                                    <td className="py-4 text-white font-medium">
                                        {pred.customerID}
                                    </td>
                                    <td className="py-4 text-text-secondary text-sm">
                                        {new Date(
                                            pred.timestamp
                                        ).toLocaleString("pl-PL")}
                                    </td>
                                    <td className="py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-28 progress-bar">
                                                <div
                                                    className={`progress-bar-fill ${
                                                        pred.churn_probability >
                                                        0.5
                                                            ? "bg-linear-to-r from-rose-500 to-pink-500"
                                                            : "bg-linear-to-r from-emerald-500 to-teal-500"
                                                    }`}
                                                    style={{
                                                        width: `${
                                                            pred.churn_probability *
                                                            100
                                                        }%`,
                                                    }}
                                                />
                                            </div>
                                            <span className="text-sm text-text-secondary font-medium min-w-[50px]">
                                                {(
                                                    pred.churn_probability * 100
                                                ).toFixed(1)}
                                                %
                                            </span>
                                        </div>
                                    </td>
                                    <td className="py-4">
                                        <span
                                            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
                                                pred.prediction === 1
                                                    ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                                    : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                            }`}
                                        >
                                            {pred.prediction === 1 ? (
                                                <>
                                                    <AlertTriangle className="w-3 h-3" />{" "}
                                                    Ryzyko odpływu
                                                </>
                                            ) : (
                                                <>
                                                    <Shield className="w-3 h-3" />{" "}
                                                    Bezpieczny
                                                </>
                                            )}
                                        </span>
                                    </td>
                                    <td className="py-4">
                                        <ChevronRight className="w-5 h-5 text-text-muted group-hover:text-primary transition-colors" />
                                    </td>
                                </motion.tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </motion.div>
        </div>
    );
};

export default Dashboard;
