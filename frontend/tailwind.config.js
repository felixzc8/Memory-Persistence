/** @type {import('tailwindcss').Config} */
module.exports = {
  // NOTE: Update this to include the paths to all files that contain Nativewind classes.
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./contexts/**/*.{js,jsx,ts,tsx}", "./lib/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: "#3679c9",
        secondary: "#111827",
        light: {
          100: "#F3F4F6"
        },
        dark: {
          100: "#111827",
          200: "#810337"
        }
      }
    },
  },
  plugins: [],
}