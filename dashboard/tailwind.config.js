/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Geist", "IBM Plex Sans", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["Geist Mono", "IBM Plex Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        ink: {
          950: "#0b0c0f",
          900: "#111318",
          800: "#181b22",
          700: "#22262f",
        },
        brass: {
          400: "#d4b483",
          500: "#c4a574",
          600: "#a88858",
        },
      },
      keyframes: {
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.45" },
        },
        drawIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        pulseSoft: "pulseSoft 2.4s ease-in-out infinite",
        drawIn: "drawIn 0.6s ease-out both",
      },
    },
  },
  plugins: [],
};
