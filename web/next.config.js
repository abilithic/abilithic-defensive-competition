/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // ESLint tidak dijadikan blocker saat build/deploy (type-checking tetap aktif).
  eslint: { ignoreDuringBuilds: true },
};
module.exports = nextConfig;
