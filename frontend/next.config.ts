import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Use standalone for Docker container; use static export for Netlify/hosting
  output: process.env.BUILD_STANDALONE === "true" ? "standalone" : "export",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
