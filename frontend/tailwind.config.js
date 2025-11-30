/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {
            colors: {
                background: "#0a0a0f",
                surface: {
                    DEFAULT: "#12121a",
                    elevated: "#1a1a24",
                },
                primary: {
                    DEFAULT: "#6366f1",
                    light: "#818cf8",
                },
                secondary: "#a855f7",
                accent: "#22d3ee",
                success: "#22c55e",
                warning: "#eab308",
                danger: "#ef4444",
                border: {
                    DEFAULT: "#27272a",
                    light: "#3f3f46",
                },
                text: {
                    primary: "#fafafa",
                    secondary: "#a1a1aa",
                    muted: "#71717a",
                },
            },
            fontFamily: {
                sans: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
            },
            animation: {
                "fade-in": "fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
                "slide-up": "slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
                float: "float 6s ease-in-out infinite",
                "pulse-slow": "pulseSlow 4s ease-in-out infinite",
            },
            keyframes: {
                fadeIn: {
                    "0%": { opacity: "0" },
                    "100%": { opacity: "1" },
                },
                slideUp: {
                    "0%": { transform: "translateY(30px)", opacity: "0" },
                    "100%": { transform: "translateY(0)", opacity: "1" },
                },
                float: {
                    "0%, 100%": { transform: "translateY(0px) rotate(0deg)" },
                    "50%": { transform: "translateY(-20px) rotate(2deg)" },
                },
                pulseSlow: {
                    "0%, 100%": { opacity: "0.4", transform: "scale(1)" },
                    "50%": { opacity: "0.6", transform: "scale(1.05)" },
                },
            },
            backdropBlur: {
                xs: "2px",
            },
        },
    },
    plugins: [],
};
