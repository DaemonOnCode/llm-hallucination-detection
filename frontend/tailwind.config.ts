import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
      colors: {
        primary: "rgb(94 23 235)",
        "primary-foreground": "#fff",
        dark: "#0e0325",
        halfdark: "#2b0a6e",
        secondary: "#8c52ff",
        destructive: "#ff005c",
        muted: "#f3eefd",
        charcoal: {
          50: "#f2f2f2",
          100: "#d9d9d9",
          200: "#bfbfbf",
          300: "#a6a6a6",
          400: "#8c8c8c",
          500: "#737373",
          600: "#595959",
          700: "#171717",
          800: "#121212",
          900: "#0d0d0d",
        },
      },
    },
  },
  plugins: [],
};
export default config;
