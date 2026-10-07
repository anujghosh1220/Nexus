import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        nexus: {
          background: "#05070D",
          surface: "#080B12",
          "surface-elevated": "#0B1020",
          primary: "#3B82F6",
          secondary: "#6366F1",
          accent: "#22D3EE",
          text: "#F8FAFC",
          "text-muted": "#94A3B8",
          border: "rgba(255,255,255,0.08)",
          "border-accent": "rgba(59,130,246,0.15)",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        nexus: "0.75rem",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        nexus: "0 0 20px rgba(59,130,246,0.15)",
        "nexus-lg": "0 0 40px rgba(59,130,246,0.25)",
      },
      animation: {
        "fade-in-up": "fadeInUp 0.6s ease-out forwards",
        "pulse-soft": "pulse-soft 2s ease-in-out infinite",
        glow: "glow 3s ease-in-out infinite",
        "grid-move": "gridMove 20s linear infinite",
        "node-float": "nodeFloat 3s ease-in-out infinite",
        "connection-pulse": "connectionPulse 2s ease-in-out infinite",
        shimmer: "shimmer 2s linear infinite",
        "border-glow": "borderGlow 2s ease-in-out infinite",
      },
      keyframes: {
        fadeInUp: {
          from: {
            opacity: "0",
            transform: "translateY(20px)",
          },
          to: {
            opacity: "1",
            transform: "translateY(0)",
          },
        },
        "pulse-soft": {
          "0%, 100%": {
            opacity: "1",
          },
          "50%": {
            opacity: "0.6",
          },
        },
        glow: {
          "0%, 100%": {
            "box-shadow": "0 0 20px rgba(59,130,246,0.15)",
          },
          "50%": {
            "box-shadow": "0 0 40px rgba(59,130,246,0.3)",
          },
        },
        gridMove: {
          "0%": {
            "background-position": "0 0",
          },
          "100%": {
            "background-position": "60px 60px",
          },
        },
        nodeFloat: {
          "0%, 100%": {
            transform: "translateY(0)",
          },
          "50%": {
            transform: "translateY(-8px)",
          },
        },
        connectionPulse: {
          "0%, 100%": {
            "stroke-opacity": "0.3",
          },
          "50%": {
            "stroke-opacity": "0.8",
          },
        },
        shimmer: {
          "0%": {
            "background-position": "-200% 0",
          },
          "100%": {
            "background-position": "200% 0",
          },
        },
        borderGlow: {
          "0%, 100%": {
            "border-color": "rgba(59,130,246,0.15)",
          },
          "50%": {
            "border-color": "rgba(59,130,246,0.4)",
          },
        },
      },
    },
  },
  plugins: [],
};

export default config;
