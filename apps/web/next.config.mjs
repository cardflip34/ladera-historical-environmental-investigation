/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The data layer reads CSV/GeoJSON from ../../research and ../../data at request time.
  experimental: {
    outputFileTracingRoot: process.cwd(),
  },
};

export default nextConfig;
