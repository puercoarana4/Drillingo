import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Drillingo streetwear palette (Req 12.1, 12.2)
        background: "#1A1A1A",
        surface: "#242424",
        accent: "#FF0033",
        foreground: "#FFFFFF",
        muted: "#6B6B6B",
        border: "#333333",
      },
      fontFamily: {
        // Req 12.3: bold streetwear typography
        display: ["Impact", "Roboto Black", "Arial Black", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      minHeight: {
        // Req 12.4: primary action buttons min 48px
        btn: "48px",
      },
      screens: {
        // Req 12.5: functional from 375px (mobile) to 1440px (desktop)
        xs: "375px",
      },
    },
  },
  plugins: [],
};

export default config;
