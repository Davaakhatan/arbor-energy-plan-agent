import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Arbor brand colors
        arbor: {
          primary: "#10B981",    // Emerald green
          secondary: "#059669",  // Darker green
          accent: "#34D399",     // Light green
          dark: "#064E3B",       // Very dark green
        },
        // Semantic colors
        savings: "#10B981",      // Green for savings
        warning: "#F59E0B",      // Amber for warnings
        danger: "#EF4444",       // Red for risks
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
