/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        moss: "#0f766e",
        copper: "#e0523f",
        cloud: "#f4f7fb"
      }
    }
  },
  plugins: []
};
