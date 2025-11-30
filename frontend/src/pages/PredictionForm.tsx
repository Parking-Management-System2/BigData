import { AnimatePresence, motion } from "framer-motion";
import {
    AlertCircle,
    Calendar,
    CheckCircle,
    CreditCard,
    DollarSign,
    FileText,
    Headphones,
    Send,
    Shield,
    Sparkles,
    User,
    Wifi,
    Wrench,
} from "lucide-react";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { submitPrediction } from "../services/api";
import type { CustomerData } from "../types";

// Move components outside to prevent re-creation on every render
const FormSection: React.FC<{
    title: string;
    icon: React.ReactNode;
    children: React.ReactNode;
}> = ({ title, icon, children }) => (
    <div className="space-y-4">
        <div className="flex items-center gap-2 text-text-secondary">
            {icon}
            <h3 className="text-sm font-semibold uppercase tracking-wider">
                {title}
            </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">{children}</div>
    </div>
);

const InputField: React.FC<{
    label: string;
    name: string;
    type?: string;
    value: string | number;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    icon?: React.ReactNode;
    suffix?: string;
}> = ({ label, name, type = "text", value, onChange, icon, suffix }) => (
    <div className="space-y-2">
        <label className="label">{label}</label>
        <div className="relative flex items-center">
            {icon && (
                <div className="absolute left-3 text-text-muted pointer-events-none">
                    {icon}
                </div>
            )}
            <input
                type={type}
                name={name}
                value={value}
                onChange={onChange}
                className={`input-field ${icon ? "has-icon" : ""} ${
                    suffix ? "has-suffix" : ""
                }`}
                required
            />
            {suffix && (
                <div className="absolute right-3 text-text-muted text-sm pointer-events-none">
                    {suffix}
                </div>
            )}
        </div>
    </div>
);

const SelectField: React.FC<{
    label: string;
    name: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
    options: { value: string; label: string }[];
    icon?: React.ReactNode;
}> = ({ label, name, value, onChange, options, icon }) => (
    <div className="space-y-2">
        <label className="label">{label}</label>
        <div className="relative flex items-center">
            {icon && (
                <div className="absolute left-3 text-text-muted pointer-events-none">
                    {icon}
                </div>
            )}
            <select
                name={name}
                value={value}
                onChange={onChange}
                className={`select-field ${icon ? "has-icon" : ""}`}
            >
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                        {opt.label}
                    </option>
                ))}
            </select>
        </div>
    </div>
);

const PredictionForm: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    const [formData, setFormData] = useState<CustomerData>({
        customerID: `KLIENT-${Math.floor(Math.random() * 10000)}`,
        tenure: 12,
        InternetService: "Fiber optic",
        OnlineSecurity: "No",
        DeviceProtection: "No",
        TechSupport: "No",
        Contract: "Month-to-month",
        PaymentMethod: "Electronic check",
        MonthlyCharges: 70.0,
        TotalCharges: 840.0,
    });

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]:
                name === "tenure" ||
                name === "MonthlyCharges" ||
                name === "TotalCharges"
                    ? Number(value)
                    : value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            await submitPrediction(formData);
            setSuccess(true);
            setTimeout(() => {
                navigate("/");
            }, 2000);
        } catch (err) {
            setError("Nie udało się przesłać predykcji. Spróbuj ponownie.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto">
            {/* Header */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-10"
            >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary-light text-sm font-medium mb-4">
                    <Sparkles className="w-4 h-4" />
                    Analiza ML w czasie rzeczywistym
                </div>
                <h1 className="text-4xl font-bold text-white mb-3">
                    Nowa predykcja
                </h1>
                <p className="text-text-secondary max-w-md mx-auto">
                    Wprowadź dane klienta, aby przeanalizować ryzyko odpływu
                    przy użyciu naszego modelu uczenia maszynowego.
                </p>
            </motion.header>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="card-glow"
            >
                <form onSubmit={handleSubmit} className="space-y-8">
                    {/* Alerts */}
                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                exit={{ opacity: 0, height: 0 }}
                                className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 flex items-center gap-3"
                            >
                                <div className="p-2 bg-rose-500/20 rounded-lg">
                                    <AlertCircle className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-medium">Wystąpił błąd</p>
                                    <p className="text-sm text-rose-400/80">
                                        {error}
                                    </p>
                                </div>
                            </motion.div>
                        )}

                        {success && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                exit={{ opacity: 0, height: 0 }}
                                className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 flex items-center gap-3"
                            >
                                <div className="p-2 bg-emerald-500/20 rounded-lg">
                                    <CheckCircle className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-medium">
                                        Predykcja przesłana pomyślnie!
                                    </p>
                                    <p className="text-sm text-emerald-400/80">
                                        Przekierowywanie do panelu głównego...
                                    </p>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Customer Info Section */}
                    <FormSection
                        title="Informacje o kliencie"
                        icon={<User className="w-4 h-4" />}
                    >
                        <InputField
                            label="ID Klienta"
                            name="customerID"
                            value={formData.customerID}
                            onChange={handleChange}
                            icon={<User className="w-4 h-4" />}
                        />
                        <InputField
                            label="Staż klienta"
                            name="tenure"
                            type="number"
                            value={formData.tenure}
                            onChange={handleChange}
                            icon={<Calendar className="w-4 h-4" />}
                            suffix="mies."
                        />
                    </FormSection>

                    {/* Services Section */}
                    <FormSection
                        title="Usługi"
                        icon={<Wifi className="w-4 h-4" />}
                    >
                        <SelectField
                            label="Usługa internetowa"
                            name="InternetService"
                            value={formData.InternetService}
                            onChange={handleChange}
                            icon={<Wifi className="w-4 h-4" />}
                            options={[
                                { value: "DSL", label: "DSL" },
                                { value: "Fiber optic", label: "Światłowód" },
                                { value: "No", label: "Brak" },
                            ]}
                        />
                        <SelectField
                            label="Typ umowy"
                            name="Contract"
                            value={formData.Contract}
                            onChange={handleChange}
                            icon={<FileText className="w-4 h-4" />}
                            options={[
                                {
                                    value: "Month-to-month",
                                    label: "Miesięczna",
                                },
                                { value: "One year", label: "Roczna" },
                                { value: "Two year", label: "Dwuletnia" },
                            ]}
                        />
                    </FormSection>

                    {/* Additional Services Section */}
                    <FormSection
                        title="Usługi dodatkowe"
                        icon={<Shield className="w-4 h-4" />}
                    >
                        <SelectField
                            label="Bezpieczeństwo online"
                            name="OnlineSecurity"
                            value={formData.OnlineSecurity}
                            onChange={handleChange}
                            icon={<Shield className="w-4 h-4" />}
                            options={[
                                { value: "Yes", label: "Tak" },
                                { value: "No", label: "Nie" },
                                {
                                    value: "No internet service",
                                    label: "Brak usługi internetowej",
                                },
                            ]}
                        />
                        <SelectField
                            label="Ochrona urządzeń"
                            name="DeviceProtection"
                            value={formData.DeviceProtection}
                            onChange={handleChange}
                            icon={<Wrench className="w-4 h-4" />}
                            options={[
                                { value: "Yes", label: "Tak" },
                                { value: "No", label: "Nie" },
                                {
                                    value: "No internet service",
                                    label: "Brak usługi internetowej",
                                },
                            ]}
                        />
                        <SelectField
                            label="Wsparcie techniczne"
                            name="TechSupport"
                            value={formData.TechSupport}
                            onChange={handleChange}
                            icon={<Headphones className="w-4 h-4" />}
                            options={[
                                { value: "Yes", label: "Tak" },
                                { value: "No", label: "Nie" },
                                {
                                    value: "No internet service",
                                    label: "Brak usługi internetowej",
                                },
                            ]}
                        />
                        <SelectField
                            label="Metoda płatności"
                            name="PaymentMethod"
                            value={formData.PaymentMethod}
                            onChange={handleChange}
                            icon={<CreditCard className="w-4 h-4" />}
                            options={[
                                {
                                    value: "Electronic check",
                                    label: "Przelew elektroniczny",
                                },
                                {
                                    value: "Mailed check",
                                    label: "Czek pocztowy",
                                },
                                {
                                    value: "Bank transfer (automatic)",
                                    label: "Przelew automatyczny",
                                },
                                {
                                    value: "Credit card (automatic)",
                                    label: "Karta kredytowa",
                                },
                            ]}
                        />
                    </FormSection>

                    {/* Billing Section */}
                    <FormSection
                        title="Rozliczenia"
                        icon={<DollarSign className="w-4 h-4" />}
                    >
                        <InputField
                            label="Opłata miesięczna"
                            name="MonthlyCharges"
                            type="number"
                            value={formData.MonthlyCharges}
                            onChange={handleChange}
                            icon={<DollarSign className="w-4 h-4" />}
                            suffix="PLN"
                        />
                        <InputField
                            label="Opłaty łączne"
                            name="TotalCharges"
                            type="number"
                            value={formData.TotalCharges}
                            onChange={handleChange}
                            icon={<DollarSign className="w-4 h-4" />}
                            suffix="PLN"
                        />
                    </FormSection>

                    {/* Submit Button */}
                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={loading || success}
                            className="btn-primary w-full flex justify-center items-center gap-2 py-4 text-base"
                        >
                            {loading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Analizowanie...
                                </>
                            ) : success ? (
                                <>
                                    <CheckCircle className="w-5 h-5" />
                                    Przesłano pomyślnie
                                </>
                            ) : (
                                <>
                                    <Send className="w-5 h-5" />
                                    Prześlij do analizy
                                </>
                            )}
                        </button>
                        <p className="text-center text-text-muted text-sm mt-4">
                            Predykcja zostanie przetworzona przez model ML i
                            pojawi się na panelu głównym.
                        </p>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default PredictionForm;
