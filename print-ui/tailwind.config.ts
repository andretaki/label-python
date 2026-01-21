import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Alliance brand colors
        'alliance-purple': '#5F59F7',
        'alliance-navy': '#0D3362',
        'alliance-charcoal': '#212325',
      },
    },
  },
  plugins: [],
}
export default config
