import clsx from "clsx";
import { Activity, LayoutDashboard, Sparkles } from "lucide-react";
import React from "react";
import { Link, useLocation } from "react-router-dom";

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const location = useLocation();

    const navItems = [
        { path: "/", label: "Panel główny", icon: LayoutDashboard },
        { path: "/predict", label: "Nowa predykcja", icon: Sparkles },
    ];

    return (
        <div className="min-h-screen bg-background text-text-primary font-sans overflow-x-hidden">
            {/* Undulating Background */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                {/* Animated blobs */}
                <div
                    className="absolute w-[800px] h-[800px] rounded-full opacity-20 blur-[120px] animate-float"
                    style={{
                        background:
                            "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
                        top: "-300px",
                        left: "-200px",
                    }}
                />
                <div
                    className="absolute w-[600px] h-[600px] rounded-full opacity-15 blur-[100px] animate-float"
                    style={{
                        background:
                            "linear-gradient(135deg, #a855f7 0%, #ec4899 100%)",
                        bottom: "-200px",
                        right: "-150px",
                        animationDelay: "-2s",
                    }}
                />
                <div
                    className="absolute w-[500px] h-[500px] rounded-full opacity-10 blur-[80px] animate-float"
                    style={{
                        background:
                            "linear-gradient(135deg, #22d3ee 0%, #6366f1 100%)",
                        top: "40%",
                        left: "30%",
                        animationDelay: "-4s",
                    }}
                />

                {/* Grid overlay */}
                <div
                    className="absolute inset-0 opacity-[0.02]"
                    style={{
                        backgroundImage: `
                            linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)
                        `,
                        backgroundSize: "100px 100px",
                    }}
                />
            </div>

            {/* Navbar */}
            <nav className="fixed top-0 left-0 right-0 z-50">
                <div className="mx-4 mt-4">
                    <div className="max-w-7xl mx-auto bg-surface-elevated/60 backdrop-blur-xl rounded-2xl border border-border/50 px-6 py-3">
                        <div className="flex items-center justify-between">
                            <Link
                                to="/"
                                className="flex items-center gap-3 group"
                            >
                                <div className="relative">
                                    <div className="absolute inset-0 bg-primary/30 blur-lg rounded-full group-hover:bg-primary/50 transition-all duration-300" />
                                    <div className="relative bg-linear-to-br from-primary to-secondary p-2 rounded-xl">
                                        <Activity className="w-5 h-5 text-white" />
                                    </div>
                                </div>
                                <div>
                                    <span className="text-lg font-bold text-white">
                                        Churn
                                        <span className="text-primary-light">
                                            Guard
                                        </span>
                                    </span>
                                    <p className="text-[10px] text-text-muted -mt-1">
                                        System predykcji odpływu
                                    </p>
                                </div>
                            </Link>

                            <div className="flex items-center gap-2">
                                {navItems.map((item) => {
                                    const Icon = item.icon;
                                    const isActive =
                                        location.pathname === item.path;
                                    return (
                                        <Link
                                            key={item.path}
                                            to={item.path}
                                            className={clsx(
                                                "flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300 text-sm font-medium",
                                                isActive
                                                    ? "bg-primary/15 text-primary-light border border-primary/30"
                                                    : "text-text-secondary hover:text-text-primary hover:bg-surface/80"
                                            )}
                                        >
                                            <Icon className="w-4 h-4" />
                                            {item.label}
                                        </Link>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-16">
                {children}
            </main>

            {/* Footer gradient line */}
            <div className="fixed bottom-0 left-0 right-0 h-px bg-linear-to-r from-transparent via-primary/30 to-transparent" />
        </div>
    );
};

export default Layout;
