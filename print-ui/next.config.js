/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable experimental features for server actions
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
}

module.exports = nextConfig
